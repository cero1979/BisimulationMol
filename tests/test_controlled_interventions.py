import unittest
from src.public_validation import LogicalModel
from src.concurrent_biomodels import LTS
from src.controlled_interventions import generate, terminal_futures, marker_persistent


class InterventionTests(unittest.TestCase):
    def test_withdrawal_changes_only_input_and_is_irreversible(self):
        model = LogicalModel('tiny',('I','X'),{'I':1,'X':1},frozenset({'I'}),
                             {'X':lambda v:v['I']},(1,0),None)
        result = generate(model,('X',),withdraw='I')
        self.assertEqual(set(result.vectors), {(1,0),(1,1),(0,0),(0,1)})
        for s,a,t in result.lts.edges:
            x,y = result.vectors[s],result.vectors[t]
            if a == 'withdraw_I':
                self.assertEqual((x[0],y[0]), (1,0))
                self.assertEqual(x[1],y[1])
            if x[0] == 0:
                self.assertEqual(y[0],0)
        with self.assertRaisesRegex(ValueError,'cap'):
            generate(model,('X',),withdraw='I',max_states=2)

    def test_multiple_fates_and_mixed_terminal_cycle_are_not_commitment(self):
        lts = LTS('fork',['0','1','2'],0,[(0,'a',1),(0,'b',2)])
        result = terminal_futures(lts,lambda s: ['naive','apoptosis','survival'][s])
        self.assertEqual(result['by_state'][0], ['apoptosis','survival'])
        cyc = LTS('cycle',['0','1'],0,[(0,'a',1),(1,'b',0)])
        result = terminal_futures(cyc,lambda s: ['apoptosis','naive'][s])
        self.assertEqual(result['by_state'][0], ['other'])
        self.assertFalse(marker_persistent(cyc,{0})[0])

    def test_reachable_marker_is_not_persistent(self):
        lts = LTS('transient',['0','1','2'],0,[(0,'a',1),(1,'b',2)])
        self.assertEqual(marker_persistent(lts,{1}), [False,False,False])
        self.assertEqual(marker_persistent(lts,{1,2}), [False,True,True])

    def test_hidden_sink_elimination_preserves_weak_behavior(self):
        from src.branching_witness import find_branching_witness
        model = LogicalModel('sink',('I','X','O'),dict(I=1,X=1,O=1),frozenset({'I'}),
                             {'X':lambda v:v['I'],'O':lambda v:v['X']},(1,0,0),None)
        full = generate(model,('X',),withdraw='I')
        reduced = generate(model,('X',),withdraw='I',omit_sinks=('O',))
        self.assertTrue(find_branching_witness(full.lts,reduced.lts)['weak_bisimilar'])
        with self.assertRaisesRegex(ValueError,'observable'):
            generate(model,('X','O'),omit_sinks=('O',))


if __name__ == '__main__':
    unittest.main()
