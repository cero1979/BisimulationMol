"""Exact finite-trace checks and independently verifiable losing-game DAGs."""
from collections import deque
from .formal_audit import game_relation, IndependentLTS


class WeakAutomaton:
    """Lazy subset closure avoids materializing every weak state/action target."""
    def __init__(self, lts):
        self.out = [[] for _ in lts.states]
        for s,a,t in lts.edges:
            self.out[s].append((a,t))
        self.alphabet = {a for _,a,_ in lts.edges if a != 'tau'}
        self.start = self.close({lts.init})

    def close(self, states):
        reached = set(states)
        todo = list(states)
        while todo:
            for action, target in self.out[todo.pop()]:
                if action == 'tau' and target not in reached:
                    reached.add(target)
                    todo.append(target)
        return frozenset(reached)

    def step(self, states, action):
        return self.close({t for s in states for a,t in self.out[s] if a == action})


def exact_traces(left, right, max_subsets=10000):
    if max_subsets < 1:
        raise ValueError('max_subsets must be positive')
    a,b = WeakAutomaton(left), WeakAutomaton(right)
    start = (a.start,b.start)
    todo, seen = deque([(start,())]), {start}
    alphabet = sorted(a.alphabet | b.alphabet)
    left_only = right_only = None
    complete = True
    while todo:
        (xs,ys), word = todo.popleft()
        if xs and not ys and left_only is None:
            left_only = list(word)
        if ys and not xs and right_only is None:
            right_only = list(word)
        for action in alphabet:
            pair = a.step(xs,action), b.step(ys,action)
            if pair not in seen:
                if len(seen) >= max_subsets:
                    complete = False
                    break
                seen.add(pair)
                todo.append((pair,word+(action,)))
        if not complete:
            break
    lr = False if left_only is not None else (True if complete else None)
    rl = False if right_only is not None else (True if complete else None)
    equality = False if False in (lr,rl) else (True if complete else None)
    return {'status': 'complete' if complete else 'inconclusive',
            'algorithm': 'epsilon-NFA subset-product BFS, all states accepting',
            'exact_trace_equal': equality, 'left_trace_included_in_right': lr,
            'right_trace_included_in_left': rl, 'left_only_trace': left_only,
            'right_only_trace': right_only, 'subset_product_states': len(seen),
            'max_subsets': max_subsets}


def _certificate(left, right, records, bisimulation, reversed_models=False):
    reasons = {tuple(item['pair']): item for item in records}
    root = (left.init,right.init)
    todo, reached = [root], set()
    while todo:
        pair = todo.pop()
        if pair in reached:
            continue
        reached.add(pair)
        todo.extend(tuple(p) for p in reasons[pair]['possible_reply_pairs'])
    return {'root': list(root), 'bisimulation': bisimulation,
            'reversed_models': reversed_models,
            'selection': 'first raw-edge challenge at minimum simultaneous elimination rank; '
                         'not a globally shortest biological explanation',
            'nodes': [reasons[p] for p in sorted(reached, key=lambda p: (-reasons[p]['round'],p))]}


def find_branching_witness(left, right, max_pairs=1000000, max_subsets=10000):
    traces = exact_traces(left,right,max_subsets)
    result = {'traces': traces, 'exact_trace_equal': traces['exact_trace_equal'],
              'left_simulated_by_right': None, 'right_simulated_by_left': None,
              'weak_bisimilar': None, 'strong_bisimilar': None,
              'classification': 'inconclusive', 'certificate': None}
    if len(left.states)*len(right.states) > max_pairs:
        result['reason'] = 'direct game pair cap exceeded'
        return result
    a,b = IndependentLTS(left), IndependentLTS(right)
    runs = [('left_simulated_by_right',a,b,False,True,False),
            ('right_simulated_by_left',b,a,False,True,True),
            ('weak_bisimilar',a,b,True,True,False),
            ('strong_bisimilar',a,b,True,False,False)]
    certificates = {}
    for key,x,y,bi,weak,rev in runs:
        relation, records = game_relation(x,y,bisimulation=bi,weak=weak)
        result[key] = (x.initial,y.initial) in relation
        if not result[key] and weak:
            l,r = (right,left) if rev else (left,right)
            certificates[key] = _certificate(l,r,records,bi,rev)
    result['classification'] = (
        'trace_mismatch' if result['exact_trace_equal'] is False else
        'simulation_failure' if not result['left_simulated_by_right'] or not result['right_simulated_by_left'] else
        'bisimulation_only_failure' if not result['weak_bisimilar'] else 'equivalent')
    for key in ('left_simulated_by_right','right_simulated_by_left','weak_bisimilar'):
        if key in certificates:
            result['failed_relation'] = key
            result['certificate'] = certificates[key]
            break
    return result


def verify_branching_witness(left, right, result):
    """Check the declared losing relation, not every other result field."""
    cert = result.get('certificate')
    if not cert:
        return False
    orientations = {'left_simulated_by_right': (False, False),
                    'right_simulated_by_left': (False, True),
                    'weak_bisimilar': (True, False)}
    failed = result.get('failed_relation')
    if failed not in orientations or result.get(failed) is not False:
        return False
    bisimulation, reversed_models = orientations[failed]
    if (cert.get('bisimulation') is not bisimulation or
            cert.get('reversed_models') is not reversed_models):
        return False
    if cert['reversed_models']:
        left,right = right,left
    a,b = IndependentLTS(left), IndependentLTS(right)
    records = {tuple(n['pair']): n for n in cert['nodes']}
    if tuple(cert['root']) != (left.init,right.init) or tuple(cert['root']) not in records:
        return False
    for (x,y), n in records.items():
        side, action, target = n['attacker_side'], n['label'], n['successor']
        if side not in ('left','right') or (side == 'right' and not cert['bisimulation']):
            return False
        if (action,target) not in (a.out[x] if side == 'left' else b.out[y]):
            return False
        replies = b.replies(y,action) if side == 'left' else a.replies(x,action)
        expected = {(target,z) if side == 'left' else (z,target) for z in replies}
        if expected != {tuple(p) for p in n['possible_reply_pairs']}:
            return False
        if any(p not in records or records[p]['round'] >= n['round'] for p in expected):
            return False
    return True
