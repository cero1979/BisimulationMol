"""Cross-artifact checks for the second revision, distinct from retained R1."""
import importlib.util
import csv
import json
import re
import unittest
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "revision_R2"


class SecondRevisionArtifactsTests(unittest.TestCase):
    def test_english_checker_preserves_published_bibliography_titles(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "sample.tex"
            text = "Modeling behavior.\n\\begin{thebibliography}{1}\nPublished modelling title.\n\\end{thebibliography}\n"
            command = [sys.executable, str(ROOT / "tools/check_jbcb_english.py"), str(path)]
            path.write_text(text)
            self.assertEqual(subprocess.run(command, capture_output=True).returncode, 0)
            path.write_text(text + "Main prose modelling.\n")
            self.assertEqual(subprocess.run(command, capture_output=True).returncode, 1)

    def test_R2_positioning(self):
        text = (SOURCE / "main_jbcb_R2.tex").read_text()
        abstract = text.split(r"\begin{abstract}")[1].split(r"\end{abstract}")[0]
        for marker in ["6/6", "42", "67,600", "HPN", "p=0.25"]:
            self.assertNotIn(marker, abstract)
        self.assertIn("DNA-damage", abstract)
        self.assertIn("0.9976", abstract)
        self.assertIn("not", abstract)
        self.assertLess(text.index("Biological comparison problem and models"),
                        text.index("Computational comparison method"))
        self.assertLess(text.index("Main result: a resolution boundary in GIM"),
                        text.index("Supporting formal and implementation checks"))

    def test_R2_is_self_contained_with_all_artwork(self):
        spec = importlib.util.spec_from_file_location("build_R2", ROOT / "scripts/build_jbcb_R2_package.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        for master, files, count in [("main_jbcb_R2.tex", module.MAIN, 4),
                                     ("Supplementary_Validation_R2.tex", module.SUPPLEMENT, 2)]:
            source = (SOURCE / master).read_text()
            figures = module.validate_source(source, files)
            self.assertEqual(len(figures), count)
            self.assertTrue(all((SOURCE / f).exists() for f in figures))
        self.assertNotIn("R1_Fig", (SOURCE / "main_jbcb_R2.tex").read_text())

    def test_R2_bibliography_follows_first_citation_order(self):
        for master in ["main_jbcb_R2.tex", "Supplementary_Validation_R2.tex"]:
            source = (SOURCE / master).read_text()
            keys = []
            for group in re.findall(r"\\cite\{([^}]+)\}", source):
                for key in group.split(","):
                    if key.strip() not in keys:
                        keys.append(key.strip())
            self.assertEqual(re.findall(r"\\bibitem\{([^}]+)\}", source), keys)

    def test_R2_response_has_all_matrix_items(self):
        response = (SOURCE / "response_to_reviewer_R2.tex").read_text()
        matrix = (SOURCE / "reviewer_comment_matrix.md").read_text()
        for i in range(1, 14):
            self.assertIn(f"R2.{i}.", response)
            self.assertIn(f"| R2.{i} |", matrix)

    def test_R2_main_validation_summary_matches_results(self):
        source = (SOURCE / "main_jbcb_R2.tex").read_text()
        summary = source.split(r"\label{sec:computational-validation}", 1)[1].split(
            r"\section{Discussion}", 1)[0]
        self.assertIn(r"\label{tab:validation-summary}", summary)
        for result in ["6/6 classes", "42/42", "32 model pairs", "three hierarchy witnesses",
                       "67,600", "12 decimal places", "not a proof", "biological validity"]:
            self.assertIn(result, summary)
        results = ROOT / "results"
        def rows(name):
            with (results / name).open(newline="") as handle:
                return list(csv.DictReader(handle))
        synthetic = rows("synthetic_benchmark.csv")
        self.assertEqual(len(synthetic), 6)
        self.assertTrue(all(r["formal_match"] == "True" for r in synthetic))
        self.assertTrue(all(r["weak_bisimilar"] == r["expected_weak_equivalent"] for r in synthetic))
        external = sum((rows(name) for name in ["mcrl2_synthetic_validation.csv",
                       "public_model_validation.csv", "hpn_dream_formal_data_validation.csv"]), [])
        self.assertEqual(len(external) * 2, 42)
        self.assertTrue(all(r[key] == "True" for r in external for key in
                            ["python_mcrl2_strong_agree", "python_mcrl2_weak_agree"]))
        for name, count in [("direction_audit_R2.json", 32), ("hierarchy_audit_R2.json", 3)]:
            records = json.loads((results / name).read_text())
            self.assertEqual(len(records), count)
            self.assertTrue(all(r["independent_oracle_agrees"] for r in records))
        exhaustive = json.loads((results / "exhaustive_formal_audit_R2.json").read_text())
        self.assertEqual(exhaustive["ordered_lts_pairs"], 67600)
        self.assertEqual(exhaustive["number_of_lts"], 260)
        self.assertTrue(exhaustive["all_checks_pass"])
        holmes = json.loads((results / "holmes_pn_gdda_external_validation.json").read_text())
        self.assertTrue(holmes["agreement_at_12_decimals"])
        self.assertAlmostEqual(holmes["absolute_score_difference"], 3.33e-16, delta=1e-18)
        response = (SOURCE / "response_to_reviewer_R2.tex").read_text()
        self.assertIn("Proposition 2 and Table 5 in Appendix A", response)
        self.assertIn("Table 4, identifying each check", response)

    def test_R2_response_does_not_refer_to_local_artifacts(self):
        for suffix in ["tex", "md"]:
            response = (SOURCE / f"response_to_reviewer_R2.{suffix}").read_text()
            self.assertNotRegex(response, r"\.(?:md|json|csv|py|ipynb|tex)\b")
            self.assertNotRegex(response, r"(?:results|revision_R2|tests|scripts)/")
            self.assertNotIn(r"\path{", response)
        response = (SOURCE / "response_to_reviewer_R2.tex").read_text()
        self.assertNotRegex(response, r"\\(?:input|include|bibliography)\s*\{")
        for evidence in [r"e_0\xrightarrow{a}e_b", r"\ell_1\xrightarrow{c}\ell_c",
                         "41,080", "4,848", "C: terminal", "0.3529", "216",
                         "not rerun for this revision"]:
            self.assertIn(evidence, response)


if __name__ == "__main__":
    unittest.main()
