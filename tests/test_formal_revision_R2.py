"""Quantifier-level regressions for the second JBCB revision."""
import unittest
from unittest.mock import patch
from src import concurrent_biomodels as cbm
from src import method_benchmark as mb
from src import formal_revision_audit as audit


class SecondRevisionAuditTests(unittest.TestCase):
    def test_independent_oracle_does_not_call_production_weak_helpers(self):
        _, left, right = audit.hierarchy_pairs()[0]
        with patch.object(cbm.LTS, "tau_closure", side_effect=AssertionError("production closure used")), \
             patch.object(cbm.LTS, "weak_step", side_effect=AssertionError("production weak step used")):
            self.assertTrue(audit.independent_predicate(left, right, bisimulation=True))
            self.assertTrue(audit.exact_trace_check(left, right)["exact_trace_equal"])

    def test_example1_exact_language_without_depth_cutoff(self):
        late, early = mb.branching_time_trap()
        expected = {(), ("a",), ("a", "b"), ("a", "c")}
        self.assertEqual(audit.acyclic_language(late), expected)
        self.assertEqual(audit.acyclic_language(early), expected)
        self.assertTrue(audit.exact_trace_check(late, early)["exact_trace_equal"])

    def test_example1_direction_and_explicit_witness(self):
        row = audit.example1_audit()
        self.assertTrue(row["early_simulated_by_late"])
        self.assertFalse(row["late_simulated_by_early"])
        self.assertFalse(row["weak_bisimilar"])
        self.assertTrue(row["independent_oracle_agrees"])
        self.assertTrue(row["existing_game_agrees"])
        self.assertTrue(row["direct_witness_check"]["valid"])
        failures = {tuple(r["pair"]): r for r in row["late_to_early_deletion_certificate"]}
        self.assertEqual(failures[1, 1]["label"], "c")
        self.assertEqual(failures[1, 2]["label"], "b")
        self.assertEqual(failures[0, 0]["possible_reply_pairs"], [[1, 1], [1, 2]])
        self.assertGreater(failures[0, 0]["round"], failures[1, 1]["round"])

    def test_three_strictness_witnesses(self):
        expected = [(False, True, True, True), (False, False, True, True),
                    (False, False, False, True)]
        keys = ("strong_bisimilar", "weak_bisimilar", "left_simulated_by_right", "right_simulated_by_left")
        for pair, values in zip(audit.hierarchy_pairs(), expected):
            row = audit.pair_audit(*pair)
            with self.subTest(case=pair[0]):
                self.assertEqual(tuple(row[k] for k in keys), values)
                self.assertTrue(row["exact_trace_equal"])
                self.assertTrue(row["independent_oracle_agrees"])

    def test_six_predeclared_classes_and_orientation(self):
        for case in mb.synthetic_cases():
            row = audit.pair_audit(case.case, case.reference, case.candidate)
            self.assertTrue(row["independent_oracle_agrees"], case.case)
            self.assertEqual(mb.classify_pair(case.reference, case.candidate)["formal_class"], case.expected_class)
        late, early = mb.branching_time_trap()
        self.assertEqual(mb.classify_pair(late, early)["formal_class"], "candidate simulated by reference")
        self.assertEqual(mb.classify_pair(early, late)["formal_class"], "reference simulated by candidate")

    def test_gim_and_rcd_primitive_directions(self):
        for interface in cbm.GIM_INTERFACE_SPECS:
            a, p = cbm.gim_models_for_interface(interface)
            row = audit.pair_audit(interface, a.reachability_lts(), p.reachability_lts())
            expected = interface != "C"
            self.assertEqual(row["weak_bisimilar"], expected)
            self.assertEqual(row["left_simulated_by_right"], expected)
            self.assertEqual(row["right_simulated_by_left"], expected)
            self.assertTrue(row["independent_oracle_agrees"])
        row = audit.pair_audit("RCD", cbm.death_animal().reachability_lts(), cbm.death_plant().reachability_lts())
        self.assertFalse(row["left_simulated_by_right"])
        self.assertTrue(row["right_simulated_by_left"])
        self.assertTrue(row["independent_oracle_agrees"])

    def test_exact_trace_checker_handles_silent_cycles(self):
        a = cbm.LTS("cycle", [0, 1], 0, [(0, "tau", 0), (0, "a", 1), (1, "a", 1)])
        b = cbm.LTS("a-star", [0], 0, [(0, "a", 0)])
        self.assertTrue(audit.exact_trace_check(a, b)["exact_trace_equal"])
        with self.assertRaises(ValueError):
            audit.acyclic_language(a)


if __name__ == "__main__":
    unittest.main()
