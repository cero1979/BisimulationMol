import json
from dataclasses import replace
from pathlib import Path
import unittest
from src.death_receptor_analysis import load_variants,OBSERVABLES
from src.controlled_interventions import generate
from src.branching_witness import find_branching_witness,verify_branching_witness
from src.concurrent_biomodels import LTS

ROOT=Path(__file__).resolve().parents[1]


class DeathReceptorResultTests(unittest.TestCase):
    def test_saved_certificate_covers_real_continuation_graphs(self):
        w=json.loads((ROOT/'results/death_receptor_branching_witness.json').read_text())
        pair=[LTS(g['name'],[str(i) for i in range(g['states'])],0,
                  [tuple(edge) for edge in g['edges']]) for g in w['local_graphs']]
        self.assertTrue(verify_branching_witness(*pair,w))
        self.assertEqual(w['common_raw_history']['raw_depth'],8)
        self.assertEqual(w['traces']['right_only_trace'],['withdraw_TNF','CASP3_down'])
        self.assertEqual(w['future_options_FB_plus'],['apoptosis'])
        self.assertEqual(w['future_options_FB_minus'],['naive'])

    def test_full_readout_models_confirm_conditioned_predicates(self):
        w=json.loads((ROOT/'results/death_receptor_branching_witness.json').read_text())
        models=load_variants()
        initial=tuple(w['shared_retained_state'].get(v,0) for v in models[0].variables)
        full=[generate(replace(m,initial=initial),OBSERVABLES,withdraw='TNF') for m in models]
        actual=find_branching_witness(full[0].lts,full[1].lts)
        for key in ('left_simulated_by_right','right_simulated_by_left','weak_bisimilar','exact_trace_equal'):
            self.assertEqual(actual[key],w[key])
        self.assertTrue(verify_branching_witness(full[0].lts,full[1].lts,actual))
        for f,g in zip(full,w['local_graphs']):
            quotient=LTS('quotient',[str(i) for i in range(g['states'])],0,[tuple(e) for e in g['edges']])
            self.assertTrue(find_branching_witness(f.lts,quotient)['weak_bisimilar'])

    def test_global_trace_disproof_is_not_mislabeled_as_equivalence(self):
        r=json.loads((ROOT/'results/death_receptor_withdrawal_comparison.json').read_text())
        self.assertFalse(r['trace_analysis']['exact_trace_equal'])
        self.assertIs(r['weak_simulations']['left_simulated_by_right'],False)
        self.assertIs(r['weak_simulations']['right_simulated_by_left'],False)
        self.assertFalse(r['weak_bisimilar'])

    def test_sustained_disproof_keeps_reverse_inclusion_unknown(self):
        r=json.loads((ROOT/'results/death_receptor_sustained_comparison.json').read_text())
        self.assertIs(r['trace_analysis']['exact_trace_equal'],False)
        self.assertIs(r['weak_simulations']['left_simulated_by_right'],False)
        self.assertIsNone(r['weak_simulations']['right_simulated_by_left'])
        self.assertIs(r['weak_bisimilar'],False)
        counts=r['trace_analysis']['known_word_prefix_counts']
        self.assertGreater(counts[0][-1],0)
        self.assertEqual(counts[1][-1],0)

    def test_sustained_positive_path_matches_original_source_rules(self):
        path=ROOT/'results/death_receptor_sustained_sparse_audit.json'
        self.assertTrue(path.is_file(), 'The verified sustained audit must ship with Journal')
        report=json.loads(path.read_text())
        self.assertTrue(report['confirmed'])
        self.assertEqual([r['accepted'] for r in report['checks']],[True,False])
        proof=report['checks'][0]
        model=load_variants()[0]
        current=model.initial
        word=[]
        for step in proof['full_28_node_path']:
            self.assertEqual(tuple(step['source_vector']),current)
            target=tuple(step['target_vector'])
            changed=[i for i,(a,b) in enumerate(zip(current,target)) if a!=b]
            self.assertEqual(len(changed),1)
            i=changed[0]; var=model.variables[i]
            self.assertNotIn(var,model.constants)
            self.assertEqual(target[i],model.rules[var](dict(zip(model.variables,current))))
            action=var+('_up' if target[i]>current[i] else '_down')
            self.assertEqual(action,step['action'])
            if var in OBSERVABLES: word.append(action)
            current=target
        self.assertEqual(word,proof['word'])
        self.assertEqual(len(proof['full_28_node_path']),53)


if __name__=='__main__':
    unittest.main()
