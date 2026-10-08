"""Prevent the missing bibliography and old-figure failures in revision uploads."""

import re
import unittest

from scripts import build_jbcb_package as package


class JbcbPackageTests(unittest.TestCase):
    def setUp(self):
        self.source = (package.SOURCE / "main_jbcb.tex").read_text(encoding="utf-8")
        self.bibliography = (
            package.ROOT / "submission_jbcb_revision" / "bibliography_jbcb.bbl"
        ).read_text(encoding="utf-8")

    def test_upload_is_self_contained_and_preserves_article(self):
        output = package.prepare_upload_source(self.source, self.bibliography)
        self.assertNotRegex(output, r"\\(?:input|include|bibliography|bibliographystyle)\s*\{")
        self.assertEqual(output.count(r"\bibitem{"), 29)
        self.assertNotIn("../../figs/", output)
        # Reverse only packaging edits to prove the scientific source is preserved.
        restored = output.replace(self.bibliography.rstrip(), package.BIBTEX_BLOCK)
        restored = restored.replace(r"\graphicspath{{./}}", r"\graphicspath{{./}{../../figs/}}")
        for old, new in package.FIGURE_NAMES.items():
            restored = restored.replace("{" + new + "}", "{" + old + "}")
        self.assertEqual(restored, self.source)

    def test_uploaded_figures_match_only_revision_filenames(self):
        output = package.prepare_upload_source(self.source, self.bibliography)
        includes = re.findall(r"\\includegraphics\[[^\]]*\]\{([^}]+)\}", output)
        self.assertEqual(set(includes), set(package.FIGURE_NAMES.values()))
        self.assertEqual(len(includes), 6)
        self.assertTrue(set(includes).isdisjoint(package.FIGURE_NAMES))
        self.assertEqual(len(package.PACKAGE_FILES), 8)

    def test_unexpected_external_input_is_rejected(self):
        source = self.source.replace(
            r"\end{document}", r"\input{missing_table}" + "\n" + r"\end{document}"
        )
        with self.assertRaisesRegex(RuntimeError, "external TeX/bibliography"):
            package.prepare_upload_source(source, self.bibliography)


if __name__ == "__main__":
    unittest.main()
