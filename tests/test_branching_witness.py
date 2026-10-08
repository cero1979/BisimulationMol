import copy
import unittest
from src.concurrent_biomodels import LTS
from src.method_benchmark import branching_time_trap
from src.formal_audit import hierarchy_pairs
from src.branching_witness import find_branching_witness, verify_branching_witness, exact_traces


class BranchingWitnessTests(unittest.TestCase):
    def test_early_late_certificate_covers_every_defender_reply(self):
        late, early = branching_time_trap()
        w = find_branching_witness(late, early)
        self.assertTrue(w['exact_trace_equal'])
        self.assertFalse(w['left_simulated_by_right'])
        self.assertTrue(w['right_simulated_by_left'])
        self.assertFalse(w['weak_bisimilar'])
        self.assertEqual(w['classification'], 'simulation_failure')
        self.assertTrue(verify_branching_witness(late, early, w))
        broken = copy.deepcopy(w)
        broken['certificate']['nodes'][0]['possible_reply_pairs'] = []
        self.assertFalse(verify_branching_witness(late, early, broken))

    def test_identity_and_trace_mismatch(self):
        a = LTS('a', ['0','1'], 0, [(0,'a',1)])
        b = LTS('b', ['0','1'], 0, [(0,'b',1)])
        self.assertEqual(find_branching_witness(a,a)['classification'], 'equivalent')
        w = find_branching_witness(a,b)
        self.assertEqual(w['classification'], 'trace_mismatch')
        self.assertEqual(w['traces']['left_only_trace'], ['a'])
        self.assertTrue(verify_branching_witness(a,b,w))

    def test_certificate_is_bound_to_the_claimed_failed_relation(self):
        late, early = branching_time_trap()
        original = find_branching_witness(late, early)
        swapped = copy.deepcopy(original)
        swapped['failed_relation'] = 'right_simulated_by_left'
        swapped['left_simulated_by_right'] = True
        swapped['right_simulated_by_left'] = False
        false_claim = copy.deepcopy(original)
        false_claim['left_simulated_by_right'] = True
        wrong_type = copy.deepcopy(original)
        wrong_type['certificate']['bisimulation'] = True
        unknown = copy.deepcopy(original)
        unknown['failed_relation'] = 'not_a_relation'
        for altered in (swapped, false_claim, wrong_type, unknown):
            with self.subTest(altered=altered['failed_relation']):
                self.assertFalse(verify_branching_witness(late, early, altered))

    def test_mutual_simulation_does_not_hide_bisimulation_only_failure(self):
        _, a, b = hierarchy_pairs()[1]
        w = find_branching_witness(a,b)
        self.assertTrue(w['left_simulated_by_right'])
        self.assertTrue(w['right_simulated_by_left'])
        self.assertEqual(w['classification'], 'bisimulation_only_failure')
        self.assertTrue(verify_branching_witness(a,b,w))

    def test_silent_cycles_and_resource_cap(self):
        a = LTS('a',['0','1'],0,[(0,'tau',0),(0,'a',1)])
        b = LTS('b',['0','1'],0,[(0,'a',1)])
        self.assertTrue(exact_traces(a,b)['exact_trace_equal'])
        result = exact_traces(a,b,max_subsets=1)
        self.assertIsNone(result['exact_trace_equal'])
        self.assertEqual(result['status'], 'inconclusive')
        w = find_branching_witness(a,b,max_pairs=1)
        self.assertIsNone(w['weak_bisimilar'])
        self.assertEqual(w['classification'], 'inconclusive')


if __name__ == '__main__':
    unittest.main()
