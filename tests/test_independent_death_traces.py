import json
from pathlib import Path
import unittest
from src.public_validation import LogicalModel
from src.death_receptor_analysis import load_variants,OBSERVABLES
from src.independent_trace_witness import accepts_model_trace


class IndependentTraceTests(unittest.TestCase):
    def test_original_rules_distinguish_withdrawal_order(self):
        m=LogicalModel('tiny',('I','X'),dict(I=1,X=1),frozenset({'I'}),
                       {'X':lambda v:v['I']},(1,0),None)
        self.assertTrue(accepts_model_trace(m,('X',),['X_up','withdraw_I','X_down'],'I')['accepted'])
        self.assertFalse(accepts_model_trace(m,('X',),['withdraw_I','X_up'],'I')['accepted'])
        self.assertIsNone(accepts_model_trace(m,('X',),['X_up'],max_states=1)['accepted'])

    def test_global_counterexamples_with_full_original_28_node_rules(self):
        root=Path(__file__).resolve().parents[1]
        result=json.loads((root/'results/death_receptor_withdrawal_trace_equivalence.json').read_text())
        plus,minus=load_variants()
        for key,expected in [('left_only_trace',(True,False)),('right_only_trace',(False,True))]:
            for model,want in zip((plus,minus),expected):
                self.assertIs(accepts_model_trace(model,OBSERVABLES,result[key],'TNF')['accepted'],want)


if __name__=='__main__':
    unittest.main()
