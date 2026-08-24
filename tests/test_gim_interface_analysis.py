"""Regression tests for the biologically predeclared GIM interfaces."""

from __future__ import annotations

import csv
import unittest

from src import concurrent_biomodels as cbm
from src import gim_interface_analysis as gim


class GimInterfaceAnalysisTests(unittest.TestCase):
    def test_three_interfaces_preserve_the_underlying_transitions(self) -> None:
        self.assertEqual(tuple(cbm.GIM_INTERFACE_SPECS), ("A", "B", "C"))
        animal_names = {t.name for t in cbm.ddr_animal().transitions}
        plant_names = {t.name for t in cbm.ddr_plant().transitions}
        for interface_id in cbm.GIM_INTERFACE_SPECS:
            animal, plant = cbm.gim_models_for_interface(interface_id)
            self.assertEqual({t.name for t in animal.transitions}, animal_names)
            self.assertEqual({t.name for t in plant.transitions}, plant_names)

    def test_interface_classifications_and_trace_diagnostics(self) -> None:
        rows = {row["interface_id"]: row for row in gim.analysis_rows(k=6)}
        self.assertEqual(rows["A"]["formal_class"], "weak_bisimulation")
        self.assertEqual(rows["B"]["formal_class"], "weak_bisimulation")
        self.assertEqual(rows["C"]["formal_class"], "not_comparable")
        self.assertEqual(rows["A"]["trace_distance_k6"], 0.0)
        self.assertEqual(rows["B"]["trace_distance_k6"], 0.0)
        self.assertAlmostEqual(rows["C"]["trace_distance_k6"], 6 / 17)

    def test_structure_and_state_spaces_do_not_change_with_interface(self) -> None:
        rows = gim.analysis_rows(k=6)
        self.assertEqual({row["animal_model_states"] for row in rows}, {13})
        self.assertEqual({row["plant_model_states"] for row in rows}, {14})
        self.assertEqual(len({row["pn_gdda_592_similarity"] for row in rows}), 1)
        self.assertTrue(
            all(not row["structure_changed_between_interfaces"] for row in rows)
        )

    def test_mechanism_resolved_interface_exposes_terminal_difference(self) -> None:
        animal, plant = cbm.gim_models_for_interface("C")
        animal_observables = animal.reachability_lts().observables
        plant_observables = plant.reachability_lts().observables
        self.assertIn("apoptosis", animal_observables)
        self.assertIn("smr_induction", plant_observables)
        self.assertIn("differentiation_or_endoreduplication", plant_observables)
        self.assertNotEqual(animal_observables, plant_observables)

    def test_machine_readable_outputs_are_generated_with_required_fields(self) -> None:
        sensitivity_path, justification_path, justification_tex_path = (
            gim.write_outputs()
        )
        self.assertTrue(sensitivity_path.is_file())
        self.assertTrue(justification_path.is_file())
        self.assertTrue(justification_tex_path.is_file())
        with sensitivity_path.open(newline="", encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))
        self.assertEqual([row["interface_id"] for row in rows], ["A", "B", "C"])
        required = {
            "predeclared_biological_rationale",
            "observable_labels",
            "animal_internal_transitions",
            "plant_internal_transitions",
            "animal_model_states",
            "plant_model_states",
            "strong_bisimulation",
            "weak_bisimulation",
            "animal_simulated_by_plant",
            "plant_simulated_by_animal",
            "formal_class",
            "trace_distance_k6",
            "pn_gdda_592_similarity",
            "result_interpretation",
            "literature_reference_keys",
        }
        self.assertTrue(required.issubset(rows[0]))


if __name__ == "__main__":
    unittest.main()
