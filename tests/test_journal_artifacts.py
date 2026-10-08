"""The accepted Journal article must be reproducible without older manuscripts."""

import importlib.util
import hashlib
import ast
import json
from pathlib import Path
import re
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]
JOURNAL = ROOT / "Journal"
TITLE = "Locating resolution-dependent behavioral correspondence in qualitative DNA-damage response models"


class JournalArtifactsTests(unittest.TestCase):
    def source(self, name):
        path = JOURNAL / name
        self.assertTrue(path.is_file(), f"Missing canonical Journal source: {name}")
        return path.read_text()

    def test_article_title_and_all_six_figures(self):
        for name, figures in [("main.tex", {f"Fig{i}.pdf" for i in range(1, 5)}),
                              ("supplement.tex", {"SFig1.pdf", "SFig2.pdf"})]:
            text = self.source(name)
            self.assertIn(TITLE, text)
            self.assertEqual(set(re.findall(r"\\includegraphics(?:\[[^]]*\])?\{([^}]+)\}", text)), figures)
            for figure in figures:
                self.assertTrue((JOURNAL / figure).is_file(), figure)
            self.assertNotRegex(text, r"\\(?:input|include|bibliography|bibliographystyle)\s*\{")

    def test_references_and_bibliography_are_self_contained(self):
        for name in ("main.tex", "supplement.tex"):
            text = self.source(name)
            labels = re.findall(r"\\label\{([^}]+)\}", text)
            self.assertEqual(len(labels), len(set(labels)))
            self.assertFalse(set(re.findall(r"\\ref\{([^}]+)\}", text)) - set(labels))
            keys = re.findall(r"\\bibitem(?:\[[^]]*\])?\{([^}]+)\}", text)
            citations = []
            for group in re.findall(r"\\cite\w*(?:\[[^]]*\])?\{([^}]+)\}", text):
                citations.extend(key.strip() for key in group.split(","))
            self.assertEqual(len(keys), len(set(keys)))
            self.assertFalse(set(citations) - set(keys))
            self.assertEqual(list(dict.fromkeys(citations)), keys)
            self.assertEqual(text.count(r"\begin{thebibliography}"), 1)

    def test_notebook_uses_current_scripts_and_has_no_legacy_dependencies(self):
        notebook = json.loads((ROOT / "notebooks/metodologia_multiescala.ipynb").read_text())
        for index, cell in enumerate(notebook["cells"]):
            text = "".join(cell["source"])
            self.assertNotRegex(text, r"revision_R|netmahib|\bR[123]\b")
            if cell["cell_type"] == "code":
                compile(text, f"cell-{index}", "exec")
                for name in re.findall(r"['\"](scripts/[^'\"]+\.py)['\"]", text):
                    self.assertTrue((ROOT / name).is_file(), name)
                self.assertFalse(any(o["output_type"] == "error" for o in cell.get("outputs", [])))

    def test_notebook_model_api_references_exist(self):
        from src import concurrent_biomodels as cbm
        notebook = json.loads((ROOT / "notebooks/metodologia_multiescala.ipynb").read_text())
        for cell in notebook["cells"]:
            if cell["cell_type"] != "code":
                continue
            for node in ast.walk(ast.parse("".join(cell["source"]))):
                if (isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name)
                        and node.value.id == "cbm"):
                    self.assertTrue(hasattr(cbm, node.attr), node.attr)

    def test_final_scientific_interpretation_is_retained(self):
        text = " ".join(self.source("main.tex").split())
        self.assertIn("12-action", text)
        self.assertIn("reverse sustained inclusion remains undecided", text)
        self.assertIn(r"$\{\epsilon\}$", text)
        self.assertNotRegex(text, r"(?i)global sustained (?:weak-)?trace (?:equivalence|equality)\s+(?:remains|is)\s+(?:computationally\s+)?unresolved")
        self.assertNotIn("not yet a separately published remote release", text)

    def test_accepted_mathematical_content_is_unchanged(self):
        text = self.source("main.tex")
        pattern = r"\\begin\{(definition|proposition|example|algorithm|theorem|proof)\}.*?\\end\{\1\}"
        blocks = [match.group(0) for match in re.finditer(pattern, text, re.S)]
        self.assertEqual(len(blocks), 19)
        self.assertEqual(hashlib.sha256("\n".join(blocks).encode()).hexdigest(),
                         "8cfb4f5851478420d697f30c5f1c88eb18fb68f33fa0617701de0debf6de02fa")

    def test_formal_audits_and_negative_results_ship_with_journal(self):
        self.source("main.tex")
        for name, count in [("direction_audit.json", 32), ("hierarchy_audit.json", 3)]:
            rows = json.loads((ROOT / "results" / name).read_text())
            self.assertEqual(len(rows), count)
            self.assertTrue(all(row["independent_oracle_agrees"] for row in rows))
        exhaustive = json.loads((ROOT / "results/exhaustive_formal_audit.json").read_text())
        self.assertTrue(exhaustive["all_checks_pass"])

    def test_flat_package_uses_only_journal_sources(self):
        path = ROOT / "scripts/build_journal.py"
        self.assertTrue(path.is_file(), "Missing standalone Journal builder")
        spec = importlib.util.spec_from_file_location("journal_builder", path)
        builder = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(builder)
        with tempfile.TemporaryDirectory() as directory:
            archive_path = Path(directory) / "Journal.zip"
            builder.write_archive(archive_path, include_pdfs=False)
            with zipfile.ZipFile(archive_path) as archive:
                self.assertIsNone(archive.testzip())
                names = archive.namelist()
                self.assertEqual(len(names), len(set(names)))
                self.assertEqual(set(names), set(builder.SOURCES))
                self.assertTrue(all("/" not in name and "\\" not in name for name in names))
                for name in names:
                    self.assertEqual(archive.read(name), (JOURNAL / name).read_bytes())


if __name__ == "__main__":
    unittest.main()
