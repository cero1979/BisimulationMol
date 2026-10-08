"""Unitary asynchronous execution with a single irreversible input withdrawal."""
from dataclasses import dataclass
from collections import deque
import networkx as nx
from .concurrent_biomodels import LTS


@dataclass
class Execution:
    lts: LTS
    variables: tuple
    vectors: list
    raw_edges: list


def generate(model, observables, withdraw=None, max_states=200000, omit_sinks=()):
    """omit_sinks requires caller verification that these nodes regulate no retained node."""
    if max_states < 1:
        raise ValueError('max_states must be positive')
    if withdraw is not None and withdraw not in model.constants:
        raise ValueError('withdrawal requires a declared fixed input')
    if set(omit_sinks) & (set(observables) | set(model.constants)):
        raise ValueError('Cannot omit observable nodes or inputs')
    states, index, edges, raw = [model.initial], {model.initial:0}, [], []
    enabled = [(i,v) for i,v in enumerate(model.variables)
               if v not in model.constants and v not in omit_sinks]
    for state in states:
        source = index[state]
        values = dict(zip(model.variables,state))
        updates = []
        for i,var in enabled:
            target = int(model.rules[var](values))
            if not 0 <= target <= model.max_levels[var]:
                raise ValueError(f'Invalid target for {var}: {target}')
            if target != state[i]:
                direction = 1 if target > state[i] else -1
                updates.append((i,state[i]+direction,f'{var}_{"up" if direction>0 else "down"}',var in observables))
        if withdraw is not None and values[withdraw] == 1:
            updates.append((model.variables.index(withdraw),0,'withdraw_'+withdraw,True))
        for i,value,action,visible in updates:
            successor = state[:i]+(value,)+state[i+1:]
            if successor not in index:
                if len(states) >= max_states:
                    raise ValueError(f'reachable state cap {max_states} exceeded')
                index[successor] = len(states)
                states.append(successor)
            target = index[successor]
            edges.append((source,action if visible else 'tau',target))
            raw.append((source,action,target))
    lts = LTS(model.name+('-withdrawal' if withdraw else '-sustained'),
              [str(i) for i in range(len(states))],0,sorted(edges))
    return Execution(lts,model.variables,states,sorted(raw))


def terminal_futures(lts, classify):
    graph = nx.DiGraph()
    graph.add_nodes_from(range(len(lts.states)))
    graph.add_edges_from((s,t) for s,_,t in lts.edges)
    condensation = nx.condensation(graph)
    mapping = condensation.graph['mapping']
    futures, terminal = {}, []
    for c in reversed(list(nx.topological_sort(condensation))):
        if condensation.out_degree(c):
            futures[c] = set().union(*(futures[t] for t in condensation.successors(c)))
        else:
            members = sorted(condensation.nodes[c]['members'])
            labels = {classify(s) for s in members}
            fate = next(iter(labels)) if len(labels) == 1 else 'other'
            futures[c] = {fate}
            terminal.append({'states':members,'size':len(members),'fate':fate})
    return {'by_state':[sorted(futures[mapping[s]]) for s in range(len(lts.states))],
            'terminal_components':sorted(terminal,key=lambda r:r['states'][0]),
            'interpretation':'reachable terminal SCC fates, not inevitability under unfair scheduling'}


def marker_persistent(lts, positive_states):
    reverse = [[] for _ in lts.states]
    for s,_,t in lts.edges:
        reverse[t].append(s)
    bad = set(range(len(lts.states))) - set(positive_states)
    todo = list(bad)
    while todo:
        for s in reverse[todo.pop()]:
            if s not in bad:
                bad.add(s)
                todo.append(s)
    return [s not in bad for s in range(len(lts.states))]


def observable_prefix(execution, target):
    """A shortest raw-update path, with its visible projection; not shortest visible word."""
    out = [[] for _ in execution.vectors]
    for s,a,t in execution.raw_edges:
        out[s].append((a,t))
    parent = {execution.lts.init:None}
    todo = deque([execution.lts.init])
    while todo and target not in parent:
        s = todo.popleft()
        for a,t in out[s]:
            if t not in parent:
                parent[t] = (s,a)
                todo.append(t)
    steps = []
    current = target
    while parent[current] is not None:
        s,a = parent[current]
        steps.append((s,a,current))
        current = s
    steps.reverse()
    visible = {(s,t):a for s,a,t in execution.lts.edges}
    return {'raw_path':steps,'observable_prefix':[visible[s,t] for s,_,t in steps if visible[s,t]!='tau']}
