"""Cross-artifact regression checks for the JBCB major revision."""

from __future__ import annotations

import unittest
from pathlib import Path

from src import gim_interface_analysis as gim


ROOT = Path(__file__).resolve().parents[1]
MANUSCRIPT = ROOT / "paper" / "jbcb" / "main_jbcb.tex"


class JbcbRevisionConsistencyTests(unittest.TestCase):
    def test_manuscript_matches_executed_gim_results(self) -> None:
        text = MANUSCRIPT.read_text(encoding="utf-8")
        rows = {row["interface_id"]: row for row in gim.analysis_rows(k=6)}
        self.assertEqual(rows["A"]["formal_class"], "weak_bisimulation")
        self.assertEqual(rows["B"]["formal_class"], "weak_bisimulation")
        self.assertEqual(rows["C"]["formal_class"], "not_comparable")
        self.assertIn("0.9976", text)
        self.assertIn("0.3529", text)
        self.assertIn("Interfaces A and B", text)
        self.assertIn("both simulation directions fail", text)

    def test_obsolete_ordinal_result_is_absent_from_public_narrative(self) -> None:
        paths = [MANUSCRIPT, ROOT / "README.md", ROOT / "REPRODUCIBILITY.md"]
        for path in paths:
            text = path.read_text(encoding="utf-8")
            self.assertNotIn("0.091", text, path)
            self.assertNotIn("0.111", text, path)
            self.assertNotIn("formal_class_spearman_rho", text, path)

    def test_revision_keeps_direction_and_evidence_boundaries_explicit(self) -> None:
        text = MANUSCRIPT.read_text(encoding="utf-8")
        normalized = " ".join(text.split())
        self.assertIn("three left-model-in-right-model", normalized)
        self.assertIn("three right-model-in-left-model", normalized)
        self.assertIn("four evidence layers", normalized)
        self.assertIn("biological validation", normalized)
        self.assertIn("Structural and behavioral comparisons", normalized)

    def test_figure_pipeline_includes_central_gim_artwork(self) -> None:
        source = (ROOT / "make_figures.py").read_text(encoding="utf-8")
        self.assertIn("def fig_gim_interface_case", source)
        self.assertIn('"Fig2.pdf"', source)
        self.assertIn('"FigS1a.pdf"', source)
        self.assertIn('"FigS1b.pdf"', source)

    def test_verified_biological_references_and_disclosure_policy(self) -> None:
        bibliography = (ROOT / "paper" / "jbcb" / "references_jbcb.bib").read_text(
            encoding="utf-8"
        )
        manuscript = MANUSCRIPT.read_text(encoding="utf-8")
        for key in (
            "JacksonBartek2009",
            "BlackfordJackson2017",
            "DeSchutter2007",
            "Yi2014",
            "Adachi2011",
            "FulcherSablowski2009",
            "Ogita2018",
            "ManovaGruszka2015",
        ):
            self.assertIn(f"@article{{{key},", bibliography)
        self.assertNotIn("Disclosure of generative AI assistance", manuscript)


if __name__ == "__main__":
    unittest.main()
