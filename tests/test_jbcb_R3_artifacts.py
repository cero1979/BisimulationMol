import re
import tempfile
import unittest
import zipfile
from pathlib import Path
from scripts.assemble_jbcb_R3 import assemble, mathematical_blocks
from scripts.build_jbcb_R2_package import validate_source
from scripts.build_jbcb_R3_package import build_reproducibility_archive

ROOT=Path(__file__).resolve().parents[1]


class ThirdRevisionArtifactsTests(unittest.TestCase):
    def test_assembly_preserves_accepted_mathematics_and_is_self_contained(self):
        assemble()
        original=(ROOT/'revision_R2/main_jbcb_R2.tex').read_text()
        current=(ROOT/'revision_R3/main_jbcb_R3.tex').read_text()
        self.assertEqual(mathematical_blocks(original),mathematical_blocks(current))
        figures=validate_source(current,[p.name for p in (ROOT/'revision_R3').iterdir()])
        self.assertEqual(set(figures),{f'R3_Fig{i}.pdf' for i in range(1,5)})
        labels=re.findall(r'\\label\{([^}]+)\}',current)
        self.assertEqual(len(labels),len(set(labels)))
        self.assertFalse(set(re.findall(r'\\ref\{([^}]+)\}',current))-set(labels))

    def test_reviewer_letter_has_no_internal_file_dependencies(self):
        text=(ROOT/'revision_R3/response_to_reviewer_R3.tex').read_text()
        self.assertNotRegex(text,r'\.(?:md|json|csv|py)\b')
        self.assertNotRegex(text,r'\\(?:input|include|bibliography)\{')

    def test_baseline_is_refuted_without_changing_conditioned_equality(self):
        for name in ('abstract','introduction','death_results','discussion','response','supplement'):
            text=(ROOT/'revision_R3/sections'/f'{name}.tex').read_text()
            self.assertNotRegex(text,r'(?is)global sustained (?:weak-)?trace (?:equivalence|equality)\s+(?:remains|is)\s+(?:computationally\s+)?unresolved')
        main=(ROOT/'revision_R3/sections/death_results.tex').read_text()
        self.assertIn('12-action',main)
        self.assertIn('reverse inclusion remains unresolved',main)
        self.assertIn(r'$\{\epsilon\}$',main)

    def test_reproducibility_bundle_contains_r3_and_retained_test_dependencies(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'repro.zip'
            report=build_reproducibility_archive(path)
            with zipfile.ZipFile(path) as archive:
                names=archive.namelist()
                self.assertEqual(len(names),len(set(names)))
                self.assertIsNone(archive.testzip())
                self.assertNotIn('revision_R3/portable_archive_check_R3.json',names)
                for name in ['src/independent_trace_witness.py',
                             'data/public_models/Calzone__Cell_Fate.zginml',
                             'results/branching_case_preregistration.json',
                             'submission_jbcb_revision/bibliography_jbcb.bbl',
                             'revision_R2/main_jbcb_R2.tex',
                             'notebooks/metodologia_multiescala.ipynb']:
                    self.assertEqual(archive.read(name),(ROOT/name).read_bytes())
                self.assertFalse(any('/literature/' in n or '__pycache__' in n for n in names))
                self.assertEqual(report['files'],len(names))


if __name__=='__main__':
    unittest.main()
