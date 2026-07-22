"""Regression tests for the formal engine and independent benchmark."""

from __future__ import annotations

import unittest

from src import concurrent_biomodels as cbm
from src import method_benchmark as mb


class SyntheticBenchmarkTests(unittest.TestCase):
    def test_predeclared_relations_are_recovered(self) -> None:
        rows = mb.validation_benchmark()
        self.assertTrue(all(row["formal_match"] for row in rows))

    def test_baselines_expose_expected_failure_modes(self) -> None:
        rows = mb.validation_benchmark()
        by_case = {row["case"]: row for row in rows}
        self.assertTrue(by_case["label order swap"]["structurally_equivalent_at_0_9"])
        self.assertFalse(by_case["label order swap"]["weak_bisimilar"])
        self.assertTrue(by_case["trace-equivalent branching"]["trace_equivalent_at_k"])
        self.assertFalse(by_case["trace-equivalent branching"]["weak_bisimilar"])
        self.assertEqual(by_case["identity"]["lts_gda_similarity"], 1.0)
        self.assertFalse(by_case["label order swap"]["lts_gda_equivalent_at_0_9"])
        self.assertTrue(by_case["label order swap"]["pn_gdda_equivalent_at_0_9"])

    def test_graphlet_baseline_improves_on_the_summary_profile(self) -> None:
        accuracy = {
            row["method"]: row["accuracy"]
            for row in mb.baseline_accuracy(mb.validation_benchmark())
        }
        self.assertGreater(
            accuracy["LTS-GDA (>=0.9)"],
            accuracy["structural profile (>=0.9)"],
        )

    def test_case_study_regression(self) -> None:
        rows = {row.module: row for row in cbm.run_full_analysis(k=6)}
        self.assertTrue(rows["GIM"].weak_bisimilar)
        self.assertTrue(rows["DCE"].weak_bisimilar)
        self.assertTrue(rows["SPS"].weak_bisimilar)
        self.assertFalse(rows["RCD"].weak_bisimilar)
        self.assertFalse(rows["AID"].weak_bisimilar)

    def test_scalability_metadata_is_deterministic(self) -> None:
        rows = mb.scalability_benchmark(sizes=(8, 16), repeats=1)
        self.assertEqual(len(rows), 4)
        self.assertTrue(all(row["candidate_relation_pairs"] > 0 for row in rows))
        self.assertTrue(all(row["total_runtime_ms"] >= 0 for row in rows))


if __name__ == "__main__":
    unittest.main()
