"""Tests for public-model import and independent mCRL2 validation."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from src import public_validation as pv


class PublicModelValidationTests(unittest.TestCase):
    def test_declared_public_files_are_unchanged(self) -> None:
        pv.verify_public_model_files()

    def test_public_models_generate_nontrivial_reachable_systems(self) -> None:
        summaries = {row["model"]: row for row in pv.public_model_summary()}
        self.assertEqual(set(summaries), {"mammalian_cell_cycle", "p53_mdm2"})
        self.assertTrue(all(row["reachable_states"] > 1 for row in summaries.values()))
        self.assertTrue(all(row["reachable_edges"] > 0 for row in summaries.values()))

    def test_public_controls_recover_predeclared_python_relations(self) -> None:
        for case in pv.public_validation_cases():
            from src import concurrent_biomodels as cbm

            self.assertEqual(
                cbm.strong_bisimilar(case.reference, case.candidate),
                case.expected_strong,
                msg=f"{case.model.source.key}: {case.case}",
            )
            self.assertEqual(
                cbm.weak_bisimilar(case.reference, case.candidate),
                case.expected_weak,
                msg=f"{case.model.source.key}: {case.case}",
            )

    def test_aut_export_has_consistent_header(self) -> None:
        _model, lts = pv.public_model_lts()["p53_mdm2"]
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "model.aut"
            pv.write_aut(lts, path)
            first_line = path.read_text(encoding="utf-8").splitlines()[0]
        self.assertEqual(first_line, f"des (0,{len(set(lts.edges))},{len(lts.states)})")

    @unittest.skipUnless(pv.find_ltscompare(required=False), "mCRL2 ltscompare not installed")
    def test_mcrl2_agrees_with_python_and_expected_relations(self) -> None:
        public_rows = pv.run_public_validation()
        synthetic_rows = pv.run_synthetic_mcrl2_validation()
        self.assertTrue(all(row["all_expected_results_match"] for row in public_rows))
        self.assertTrue(all(row["python_mcrl2_strong_agree"] for row in synthetic_rows))
        self.assertTrue(all(row["python_mcrl2_weak_agree"] for row in synthetic_rows))
        self.assertTrue(all(row["mcrl2_trace_matches_predeclared"] for row in synthetic_rows))


if __name__ == "__main__":
    unittest.main()
