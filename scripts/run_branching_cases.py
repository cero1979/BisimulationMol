"""Reproduce the Journal endpoint-matched death-receptor commitment comparison.

Large deterministic graphs are regenerated, not loaded from Python pickle files.
Optional raw AUT exports permit independent full-graph mCRL2 checks.
"""
import argparse
from collections import deque
from dataclasses import replace
import csv
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import numpy as np
import networkx as nx
from numba import njit

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from src.death_receptor_analysis import (load_variants, configuration, config_hash,
    regulatory_dependencies, OBSERVABLES, SUSTAINED_COUNTEREXAMPLE)
from src.compact_execution import (compact_generate, compact_futures, compact_trace_check,
    compact_step, decode_fates, persistent_states)
from src.controlled_interventions import generate, observable_prefix, terminal_futures
from src.branching_witness import find_branching_witness, verify_branching_witness
from src.independent_trace_witness import accepts_model_trace
from src.public_validation import compare_with_mcrl2, find_ltscompare, mcrl2_version
from src import concurrent_biomodels as cbm

SINKS = ('NonACD','Apoptosis','Survival')


def fate_codes(e):
    a,s,m,at = (e.values(v) for v in ('CASP3','NFkB','MPT','ATP'))
    codes = np.full(len(a),4,np.int8)
    codes[(a==0)&(s==0)&(m==0)&(at==1)] = 0
    codes[(a==0)&(s==1)&(m==0)] = 1
    codes[(a==1)&(s==0)&(m==0)] = 2
    codes[(a==0)&(s==0)&(m==1)&(at==0)] = 3
    return codes


def recode(source,target,withdraw=False):
    bits = np.zeros(len(source.bits),np.uint32)
    for i,var in enumerate(target.active):
        values = 0 if withdraw and var=='TNF' else source.values(var)
        bits |= np.asarray(values,dtype=np.uint32)<<i
    lookup = np.full(1<<len(target.active),-1,np.int32)
    lookup[target.bits] = np.arange(len(target.bits))
    return lookup[bits]


@njit(cache=True)
def next_layer(offsets,targets,layer):
    reached = np.zeros(len(offsets)-1,np.bool_)
    for s in layer:
        for edge in range(offsets[s],offsets[s+1]):
            reached[targets[edge]] = True
    return np.flatnonzero(reached).astype(np.int32)


def compact_prefix(e,target):
    parent = {0:None}
    todo = [0]
    for s in todo:
        for edge in range(e.offsets[s],e.offsets[s+1]):
            t = int(e.targets[edge])
            if t not in parent:
                var = e.active[int(e.changed[edge])]
                value = int((e.bits[t] >> int(e.changed[edge]))&1)
                parent[t] = (s,var+('_up' if value else '_down'),e.actions[int(e.labels[edge])])
                todo.append(t)
        if target in parent:
            break
    steps,current = [],target
    while parent[current] is not None:
        s,raw,visible = parent[current]
        steps.append({'source':s,'action':raw,'visible':visible,'target':current})
        current = s
    steps.reverse()
    return {'raw_path':steps,'raw_depth':len(steps),
            'observable_prefix':[step['visible'] for step in steps if step['visible']!='tau']}


def write_json(name,data,provenance):
    (ROOT/'results'/name).write_text(json.dumps(dict(provenance,**data),indent=2,sort_keys=True)+'\n')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--export-aut',action='store_true')
    args = parser.parse_args()
    frozen = json.loads((ROOT/'results/branching_case_preregistration.json').read_text())
    assert frozen['configuration']==configuration()
    provenance = {'configuration_sha256':config_hash(configuration()),
                  'amendments':['branching_case_amendment_01.json','branching_case_amendment_02.json',
                                'branching_case_amendment_03.json'],
                  'scope':'exact hidden-sink quotient of the public full Boolean model',
                  'omitted_hidden_sinks':list(SINKS)}
    models = load_variants()
    dependencies = regulatory_dependencies()
    assert not any(set(regs)&set(SINKS) for regs in dependencies.values())
    base,controlled,futures = [],[],[]
    summaries,scan = {},[]
    for model in models:
        per = {}
        for protocol in ('sustained','withdrawal'):
            e = compact_generate(model,OBSERVABLES,dependencies,
                                 withdraw='TNF' if protocol=='withdrawal' else None,omit_sinks=SINKS)
            f = compact_futures(e,fate_codes(e),expanded=False)
            summary = {'states':len(e.bits),'edges':len(e.targets),
                       'initial_reachable_terminal_fates':decode_fates(f['masks'][0]),
                       'terminal_components':f['terminal_components'],
                       'graph_sha256':hashlib.sha256(b''.join(a.tobytes() for a in
                           (e.bits,e.offsets,e.targets,e.labels))).hexdigest()}
            per[protocol] = summary
            print(model.name,protocol,summary['states'],summary['edges'],
                  summary['initial_reachable_terminal_fates'],flush=True)
            if args.export_aut:
                directory = ROOT/'tmp/Journal'
                directory.mkdir(parents=True,exist_ok=True)
                side = 'plus' if model.name=='DR-FB+' else 'minus'
                e.write_aut(directory/(side+'-'+protocol+'.aut'))
            if protocol=='sustained':
                base.append(e)
            else:
                controlled.append(e)
                futures.append(f)
        summaries[model.name] = per
    maps = [recode(b,c,withdraw=True) for b,c in zip(base,controlled)]
    assert all(np.all(indices>=0) for indices in maps)
    persistent = [persistent_states(e,e.values('CASP3')==1) for e in controlled]
    for b,c,f,idx,per in zip(base,controlled,futures,maps,persistent):
        layer = np.array([0],np.int32)
        for depth in range(41):
            masks = f['masks'][idx[layer]]
            union = int(np.bitwise_or.reduce(masks,initial=0))
            scan.append({'prefix_or_step':depth,'model':b.name,'TNF_status':0,
                         'reachable_states_before_withdrawal':len(layer),
                         **{'reachable_'+fate:int(fate in decode_fates(union)) for fate in
                            ('naive','survival','apoptosis','necrosis')},
                         'states_with_unique_terminal_apoptosis':int(np.sum(masks==4)),
                         'states_with_persistent_CASP3':int(np.sum(per[idx[layer]])),
                         'committed_fate_if_any':'state-specific; not a population probability',
                         'observable_state':'aggregate of all states at exactly this raw-event depth'})
            layer = next_layer(b.offsets,b.targets,layer)
    with (ROOT/'results/death_receptor_commitment_scan.csv').open('w') as handle:
        writer = csv.DictWriter(handle,fieldnames=list(scan[0]))
        writer.writeheader(); writer.writerows(scan)
    common = recode(base[0],base[1])
    valid = common>=0
    candidates = np.flatnonzero(valid & (base[0].values('CASP3')==1) &
                               (futures[0]['masks'][maps[0]]==4) & persistent[0][maps[0]])
    chosen = next(int(i) for i in candidates if
                  futures[1]['masks'][maps[1][common[i]]] == 1)
    other = int(common[chosen])
    prefix = compact_prefix(base[0],chosen)
    vector = base[0].vector(chosen)
    assert vector==base[1].vector(other)
    # Check the identical raw update path in the second variant, not only the endpoint.
    current = 0
    for step in prefix['raw_path']:
        next_vector = base[0].vector(step['target'])
        matches = [int(base[1].targets[k]) for k in range(base[1].offsets[current],base[1].offsets[current+1])
                   if base[1].vector(int(base[1].targets[k]))==next_vector]
        assert len(matches)==1
        current = matches[0]
    assert current==other
    local = [generate(replace(m,initial=vector),OBSERVABLES,withdraw='TNF',omit_sinks=SINKS) for m in models]
    local_baseline = [generate(replace(m,initial=vector),OBSERVABLES,omit_sinks=SINKS) for m in models]
    baseline_witness = find_branching_witness(local_baseline[0].lts,local_baseline[1].lts)
    baseline_external = compare_with_mcrl2(local_baseline[0].lts,local_baseline[1].lts)
    witness = find_branching_witness(local[0].lts,local[1].lts)
    local_acyclic = [nx.is_directed_acyclic_graph(nx.DiGraph((s,t) for s,_,t in e.lts.edges)) for e in local]
    assert verify_branching_witness(local[0].lts,local[1].lts,witness)
    production = {'left_simulated_by_right':cbm.weak_simulates(local[0].lts,local[1].lts),
                  'right_simulated_by_left':cbm.weak_simulates(local[1].lts,local[0].lts),
                  'weak_bisimilar':cbm.weak_bisimilar(local[0].lts,local[1].lts),
                  'strong_bisimilar':cbm.strong_bisimilar(local[0].lts,local[1].lts)}
    assert all(witness[k]==v for k,v in production.items())
    external = compare_with_mcrl2(local[0].lts,local[1].lts)
    for key in ('weak_bisimilar','strong_bisimilar'):
        assert external['mcrl2_'+key]==witness[key]
    assert external['mcrl2_weak_trace_equivalent']==witness['exact_trace_equal']
    aggregates = {}
    for b,c,f in zip(base,controlled,futures):
        states = compact_step(b,[0])
        for action in prefix['observable_prefix']:
            states = compact_step(b,states,action)
        post = recode(b,c,withdraw=True)[states]
        aggregates[b.name] = {'compatible_states_before_withdrawal':len(states),
                             'reachable_terminal_fates_after_withdrawal':decode_fates(
                                 np.bitwise_or.reduce(f['masks'][post],initial=0))}
    witness.update({'scope':'continuation systems rooted at a shared reachable hidden state, not the original initial states',
                    'common_observable_prefix':prefix['observable_prefix'], 'common_raw_history':prefix,
                    'left_state':chosen,'right_state':other,
                    'shared_retained_state':{k:v for k,v in zip(base[0].variables,vector) if k not in SINKS},
                    'shared_observations':{v:vector[base[0].variables.index(v)] for v in OBSERVABLES},
                    'intervention':'withdraw_TNF',
                    'future_options_FB_plus':decode_fates(futures[0]['masks'][maps[0][chosen]]),
                    'future_options_FB_minus':decode_fates(futures[1]['masks'][maps[1][other]]),
                    'history_aggregated_futures':aggregates,
                    'conditioned_sustained':dict(baseline_witness,
                        graphs=[{'states':len(e.vectors),'edges':len(e.lts.edges)} for e in local_baseline],
                        external_mcrl2=baseline_external),
                    'conditioned_graphs_acyclic':local_acyclic,
                    'local_graphs':[{'name':e.lts.name,'states':len(e.vectors),'edges':e.lts.edges,
                                     'vectors':e.vectors} for e in local],
                    'external_mcrl2':dict(version=mcrl2_version(),**external),
                    'production_predicates':production,
                    'biological_interpretation':'Feedback supports persistent CASP3 after withdrawal at this shared state; '
                                              'without feedback the only reachable terminal fate is naive. '
                                              'The three-marker history alone does not identify the hidden state.',
                    'failed_matching_action':'CASP3_down',
                    'formal_relation_that_fails':'DR-FB- <=_w DR-FB+ for the conditioned continuations'})
    write_json('death_receptor_branching_witness.json',witness,provenance)
    for name,pair in [('sustained',base),('withdrawal',controlled)]:
        traces = (compact_trace_check(*pair,max_subsets=100000,max_bytes=2000000000,max_seconds=600)
                  if name=='sustained' else compact_trace_check(*pair))
        if name=='sustained':
            counts=[]
            for execution in pair:
                states=compact_step(execution,[0])
                sizes=[len(states)]
                for action in SUSTAINED_COUNTEREXAMPLE:
                    states=compact_step(execution,states,action)
                    sizes.append(len(states))
                counts.append(sizes)
            assert counts[0][-1]>0 and counts[1][-1]==0
            # A verified finite word decides inequality even if discovery hits a cap.
            traces.update(exact_trace_equal=False,left_trace_included_in_right=False,
                          left_only_trace=list(SUSTAINED_COUNTEREXAMPLE),
                          known_word_prefix_counts=counts,
                          decision_basis='exact finite-word acceptance, not resource exhaustion')
        directions = {
            'left_simulated_by_right':False if traces['left_trace_included_in_right'] is False else None,
            'right_simulated_by_left':False if traces['right_trace_included_in_left'] is False else None}
        disproof = any(value is False for value in directions.values())
        print(name,'trace status',traces,flush=True)
        write_json('death_receptor_'+name+'_comparison.json',
                   {'graphs':{k:v[name] for k,v in summaries.items()},'trace_analysis':traces,
                    'weak_simulations':dict(directions,
                        status='exact trace counterexamples refute the indicated simulations; null means inconclusive'),
                    'weak_bisimilar':False if disproof else None,
                    'strong_bisimilar':False if disproof else None,
                    'relation_basis':'weak simulation implies weak trace inclusion; direct game exceeds pair cap'},provenance)
        write_json('death_receptor_'+name+'_trace_equivalence.json',traces,provenance)
        if name == 'withdrawal':
            independent = []
            for key, expected in [('left_only_trace', (True, False)),
                                  ('right_only_trace', (False, True))]:
                word = traces[key]
                assert word is not None, 'Expected a computed global counterexample'
                for model, accepted in zip(models, expected):
                    check = accepts_model_trace(model, OBSERVABLES, word, 'TNF')
                    assert check['accepted'] is accepted
                    independent.append(dict(model=model.name, trace=word, **check))
            write_json('death_receptor_independent_trace_audit.json',
                       {'method': 'independent full 28-node tuple/product search using original rules, '
                                  'without compact execution or sink reduction',
                        'checks': independent},
                       {'configuration_sha256': config_hash(configuration()),
                        'scope': 'original full 28-node models; no sink reduction'})
    write_json('death_receptor_trace_equivalence.json',
               {'sustained':json.loads((ROOT/'results/death_receptor_sustained_trace_equivalence.json').read_text()),
                'withdrawal':json.loads((ROOT/'results/death_receptor_withdrawal_trace_equivalence.json').read_text()),
                'conditioned_continuations':witness['traces']},provenance)
    write_json('death_receptor_execution_summary.json',
               {'models':summaries,'selected_state':chosen,'common_raw_depth':prefix['raw_depth'],
                'common_observable_prefix':prefix['observable_prefix'],
                'selection':'Pattern B: exact baseline terminal-fate agreement, intervention-dependent continuations; '
                            'not an established equal-global-trace/different-branching example',
                'candidate_2_status':'subsequent separate feasibility probe found unequal traces for the '
                    '2006/2016 cell-cycle pair; not used as branching-only biological evidence',
                'scan_horizon':40,'scan_semantics':'all histories with exactly k internal-component updates before withdrawal; '
                    'terminal states are not artificially padded; complete reachable futures after withdrawal'},provenance)


if __name__=='__main__':
    main()
