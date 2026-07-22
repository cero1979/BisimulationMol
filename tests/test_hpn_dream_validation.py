"""Regression and anti-leakage tests for the public HPN-DREAM validation."""

from __future__ import annotations

import unittest
from unittest import mock

from src import hpn_dream_validation as hpn


class HpnDreamValidationTests(unittest.TestCase):
    def test_artifacts_match_pinned_public_commit(self) -> None:
        hpn.verify_artifacts()

    def test_structure_only_medoid_selection_is_stable(self) -> None:
        expected = {
            "BT20": (72, 24, 29),
            "BT549": (191, 137, 25),
            "MCF7": (21, 9, 23),
        }
        for cell, values in expected.items():
            medoid = hpn.select_medoid(cell)
            self.assertEqual(
                (medoid.family_size, medoid.row_index, len(medoid.clauses)), values
            )

    def test_medoid_selection_cannot_read_heldout_test(self) -> None:
        original_open = hpn.Path.open

        def guarded_open(path, *args, **kwargs):
            if str(path).endswith("_test.csv"):
                raise AssertionError("held-out test leakage")
            return original_open(path, *args, **kwargs)

        with mock.patch.object(hpn.Path, "open", guarded_open):
            for cell in hpn.CELLS:
                hpn.select_medoid(cell)

    def test_predeclared_conditions_and_interface_exist_in_all_tests(self) -> None:
        for cell in hpn.CELLS:
            for condition in hpn.COMMON_CONDITIONS:
                experiment = hpn.get_experiment(cell, condition)
                self.assertIn(0, experiment.observations)
                for node in hpn.INTERFACE:
                    self.assertIn(node, experiment.observations[0])

    def test_data_conditioned_lts_is_finite_and_deterministic(self) -> None:
        medoid = hpn.select_medoid("BT20")
        model = hpn.model_from_medoid(medoid)
        experiment = hpn.get_experiment("BT20", hpn.COMMON_CONDITIONS[1])
        first = hpn.asynchronous_lts(model, experiment)
        second = hpn.asynchronous_lts(model, experiment)
        self.assertGreater(len(first.states), 0)
        self.assertEqual(first.states, second.states)
        self.assertEqual(first.edges, second.edges)

    def test_exact_concordance_null_has_216_stratified_permutations(self) -> None:
        rows = hpn.validation_rows(use_mcrl2=False)
        result = hpn.concordance_test(rows)
        self.assertEqual(len(rows), 9)
        self.assertTrue(
            all(0 not in map(int, row["common_times"].split(";")) for row in rows)
        )
        self.assertEqual(result["null_permutations"], 216)
        self.assertGreaterEqual(result["formal_class_exact_permutation_p_one_sided"], 0)
        self.assertLessEqual(result["formal_class_exact_permutation_p_one_sided"], 1)
        self.assertIn("graphlet_distance_exact_permutation_p_one_sided", result)

    def test_synchronous_stress_preserves_seven_of_nine_classes(self) -> None:
        rows = hpn.semantic_sensitivity_rows()
        self.assertEqual(len(rows), 9)
        self.assertEqual(sum(bool(row["class_preserved"]) for row in rows), 7)
        self.assertEqual(
            sum(
                row["asynchronous_class"] == "one_way_simulation"
                and row["synchronous_class"] == "not_comparable"
                for row in rows
            ),
            2,
        )

    def test_mcrl2_agrees_on_all_data_conditioned_decisions(self) -> None:
        rows = hpn.validation_rows(use_mcrl2=True)
        self.assertTrue(all(row["python_mcrl2_strong_agree"] for row in rows))
        self.assertTrue(all(row["python_mcrl2_weak_agree"] for row in rows))


if __name__ == "__main__":
    unittest.main()
