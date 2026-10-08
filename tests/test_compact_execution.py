import unittest
from src.public_validation import LogicalModel
from src.controlled_interventions import generate, terminal_futures
from src.compact_execution import compact_generate, compact_futures, compact_trace_check


class CompactExecutionTests(unittest.TestCase):
    def test_compact_execution_matches_independent_tuple_enumerator(self):
        for feedback in (False,True):
            m = LogicalModel('tiny',('I','X','Y'),dict(I=1,X=1,Y=1),frozenset({'I'}),
                             {'X':lambda v:int(v['I'] or (feedback and v['Y'])),
                              'Y':lambda v:v['X']},(1,0,0),None)
            dependencies = {'X':('I','Y'), 'Y':('X',)}
            for withdraw in (None,'I'):
                reference = generate(m,('X',),withdraw=withdraw)
                compact = compact_generate(m,('X',),dependencies,withdraw=withdraw)
                self.assertEqual([compact.vector(i) for i in range(len(compact.bits))],reference.vectors)
                self.assertEqual(sorted(compact.small_lts().edges),reference.lts.edges)
                facts = compact_futures(compact,lambda v:'apoptosis' if v[1] else 'naive')
                expected = terminal_futures(reference.lts,lambda s:'apoptosis' if reference.vectors[s][1] else 'naive')
                self.assertEqual(facts['by_state'], expected['by_state'])

    def test_compact_futures_mixed_cycle_and_cap(self):
        m = LogicalModel('cycle',('X',),{'X':1},frozenset(),{'X':lambda v:1-v['X']},(0,),None)
        e = compact_generate(m,('X',),{'X':('X',)})
        self.assertEqual(compact_futures(e,lambda v:'apoptosis' if v[0] else 'naive')['by_state'], [['other'],['other']])
        with self.assertRaisesRegex(ValueError,'cap'):
            compact_generate(m,('X',),{'X':('X',)},max_states=1)

    def test_compact_exact_traces_and_cap(self):
        m = LogicalModel('tiny',('I','X'),dict(I=1,X=1),frozenset({'I'}),
                         {'X':lambda v:v['I']},(1,0),None)
        e = compact_generate(m,('X',),{'X':('I',)})
        self.assertTrue(compact_trace_check(e,e)['exact_trace_equal'])
        self.assertIsNone(compact_trace_check(e,e,max_subsets=1)['exact_trace_equal'])
        from dataclasses import replace
        other = compact_generate(replace(m,rules={'X':lambda v:0}),('X',),{'X':('I',)})
        self.assertEqual(compact_trace_check(e,other)['left_only_trace'],['X_up'])

    def test_two_counterexamples_resolve_both_inclusions_without_exhaustion(self):
        from dataclasses import replace
        m = LogicalModel('two',('X','Y'),dict(X=1,Y=1),frozenset(),
                         {'X':lambda v:1,'Y':lambda v:0},(0,0),None)
        a = compact_generate(m,('X','Y'),{'X':(),'Y':()})
        b = compact_generate(replace(m,rules={'X':lambda v:0,'Y':lambda v:1}),
                             ('X','Y'),{'X':(),'Y':()})
        result = compact_trace_check(a,b)
        self.assertEqual(result['status'],'disproved')
        self.assertFalse(result['left_trace_included_in_right'])
        self.assertFalse(result['right_trace_included_in_left'])
        self.assertFalse(result['exact_trace_equal'])


if __name__ == '__main__':
    unittest.main()
