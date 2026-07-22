"""Regression tests for the direct PN-GDDA implementation."""

from __future__ import annotations

import unittest

from src import method_benchmark as mb
from src import pn_gdda


class PNGDDATests(unittest.TestCase):
    def test_published_catalog_has_151_graphlets_and_592_slots(self) -> None:
        summary = pn_gdda.catalog_summary(holmes_compatible=True)
        self.assertEqual(
            [(row["graphlets"], row["orbits"]) for row in summary],
            [(2, 4), (6, 14), (23, 72), (120, 502)],
        )
        self.assertEqual(sum(row["graphlets"] for row in summary), 151)
        self.assertEqual(sum(row["orbits"] for row in summary), 592)

    def test_automorphism_sensitivity_catalog_has_576_orbits(self) -> None:
        summary = pn_gdda.catalog_summary(holmes_compatible=False)
        self.assertEqual(sum(row["graphlets"] for row in summary), 151)
        self.assertEqual(sum(row["orbits"] for row in summary), 576)
        self.assertEqual(summary[-1]["orbits"], 486)

    def test_independent_score_matches_holmes_reference(self) -> None:
        validation = pn_gdda.catalog_validation()
        self.assertTrue(validation["score_agreement_at_12_decimals"])
        self.assertAlmostEqual(
            validation["independent_python_score"],
            pn_gdda.HOLMES_REFERENCE_SCORE,
            places=15,
        )

    def test_direct_baseline_exposes_topology_only_false_positives(self) -> None:
        rows = mb.validation_benchmark()
        by_case = {row["case"]: row for row in rows}
        self.assertEqual(by_case["identity"]["pn_gdda_592_similarity"], 1.0)
        self.assertEqual(by_case["label mismatch"]["pn_gdda_592_similarity"], 1.0)
        self.assertFalse(by_case["label mismatch"]["weak_bisimilar"])

        accuracy = {
            row["method"]: row for row in mb.baseline_accuracy(rows)
        }["PN-GDDA-592 (>=0.9)"]
        self.assertAlmostEqual(accuracy["accuracy"], 2 / 6)
        self.assertEqual(accuracy["false_positive"], 4)
        self.assertEqual(accuracy["false_negative"], 0)

        sensitivity = mb.pn_gdda_threshold_sensitivity(rows)
        self.assertAlmostEqual(max(row["accuracy"] for row in sensitivity), 4 / 6)
        self.assertTrue(
            all(
                row["false_positive"] >= 2
                for row in sensitivity
                if row["false_negative"] == 0
            )
        )

    def test_native_module_sensitivity_does_not_change_threshold_decisions(self) -> None:
        rows = pn_gdda.native_module_comparisons()
        self.assertEqual(len(rows), 5)
        self.assertTrue(all(row["pn_gdda_equivalent_at_0_9"] for row in rows))
        self.assertTrue(
            all(abs(row["catalog_sensitivity_delta"]) < 0.001 for row in rows)
        )


if __name__ == "__main__":
    unittest.main()
