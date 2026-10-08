import itertools
import unittest

from src.death_receptor_analysis import load_variants, configuration, validate_download


class DeathReceptorImportTests(unittest.TestCase):
    def test_feedback_removal_changes_only_casp8_input(self):
        plus, minus = load_variants()
        for d1, d2, c3, flip in itertools.product((0, 1), repeat=4):
            values = dict(DISC_TNF=d1, DISC_FAS=d2, CASP3=c3, cFLIP=flip)
            self.assertEqual(plus.rules['CASP8'](values), int((d1 or d2 or c3) and not flip))
            self.assertEqual(minus.rules['CASP8'](values), int((d1 or d2) and not flip))
            self.assertEqual(values['CASP3'], c3)
        for key in plus.rules:
            if key != 'CASP8':
                self.assertIs(plus.rules[key], minus.rules[key])
        self.assertNotIn('CASP3', minus.constants)

    def test_explicit_physiological_inputs_and_shared_interface(self):
        plus, minus = load_variants()
        self.assertEqual(plus.initial, minus.initial)
        self.assertEqual({k for k,v in zip(plus.variables, plus.initial) if v},
                         {'ATP', 'cIAP', 'TNF', 'FADD'})
        self.assertEqual(plus.constants, frozenset({'TNF', 'FASL', 'FADD'}))
        config = configuration()
        self.assertEqual(config['interface']['observable_components'], ['NFkB', 'CASP3', 'MPT'])
        self.assertEqual(set(config['interface']['hidden_components']) |
                         set(config['interface']['observable_components']), set(plus.variables))

    def test_download_rejects_changed_source(self):
        with self.assertRaisesRegex(ValueError, 'SHA-256'):
            validate_download(b'not the model')


if __name__ == '__main__':
    unittest.main()
