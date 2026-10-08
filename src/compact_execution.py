"""Memory-bounded Boolean enumeration; rules are compiled from importer truth tables."""
from dataclasses import dataclass
import itertools
import time
import numpy as np
from numba import njit
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import connected_components
from .concurrent_biomodels import LTS

FATES = ('naive','survival','apoptosis','necrosis','other')


@njit(cache=True)
def _target(state, r, positions, constants, counts, tables):
    code = 0
    for j in range(counts[r]):
        p = positions[r,j]
        value = constants[r,j] if p < 0 else (state >> p) & 1
        code |= value << j
    return tables[r,code]


@njit(cache=True)
def _enumerate(initial, nbits, rule_positions, dep_positions, constants, counts, tables,
               visible, withdrawal_position, max_states):
    index = np.full(1 << nbits,-1,np.int32)
    capacity = min(1 << nbits,max_states)
    states = np.empty(capacity,np.uint32)
    offsets = np.empty(capacity+1,np.int64)
    states[0],index[initial] = initial,0
    n, head, edges = 1,0,0
    while head < n:
        state = states[head]
        offsets[head] = edges
        for r in range(len(rule_positions)+1):
            if r < len(rule_positions):
                p = rule_positions[r]
                value = _target(state,r,dep_positions,constants,counts,tables)
                if value == ((state >> p) & 1):
                    continue
            else:
                p = withdrawal_position
                if p < 0 or ((state >> p) & 1) == 0:
                    continue
            successor = state ^ (1 << p)
            if index[successor] < 0:
                if n == capacity:
                    raise ValueError('compact reachable state cap exceeded')
                index[successor] = n
                states[n] = successor
                n += 1
            edges += 1
        head += 1
    offsets[n] = edges
    targets = np.empty(edges,np.int32)
    labels = np.empty(edges,np.int16)
    changed = np.empty(edges,np.int16)
    edge = 0
    for s in range(n):
        state = states[s]
        for r in range(len(rule_positions)+1):
            if r < len(rule_positions):
                p = rule_positions[r]
                value = _target(state,r,dep_positions,constants,counts,tables)
                if value == ((state >> p) & 1):
                    continue
                action = visible[r,1 if value else 0]
            else:
                p = withdrawal_position
                if p < 0 or ((state >> p) & 1) == 0:
                    continue
                action = visible[-1,0]
            targets[edge] = index[state ^ (1 << p)]
            labels[edge] = action
            changed[edge] = p
            edge += 1
    return states[:n].copy(), offsets[:n+1].copy(), targets,labels,changed


@dataclass
class CompactExecution:
    name: str
    variables: tuple
    active: tuple
    fixed: tuple
    bits: np.ndarray
    offsets: np.ndarray
    targets: np.ndarray
    labels: np.ndarray
    changed: np.ndarray
    actions: tuple

    def vector(self, state):
        values = dict(self.fixed)
        values.update({v:int((self.bits[state]>>i)&1) for i,v in enumerate(self.active)})
        return tuple(values[v] for v in self.variables)

    def values(self, variable):
        if variable in self.active:
            return (self.bits >> self.active.index(variable)) & 1
        return np.full(len(self.bits),dict(self.fixed)[variable],np.uint32)

    def small_lts(self):
        if len(self.bits) > 10000:
            raise ValueError('Use CSR or AUT for large compact executions')
        edges = [(s,self.actions[int(self.labels[e])],int(self.targets[e]))
                 for s in range(len(self.bits)) for e in range(self.offsets[s],self.offsets[s+1])]
        return LTS(self.name,[str(i) for i in range(len(self.bits))],0,edges)

    def sources(self):
        return np.repeat(np.arange(len(self.bits),dtype=np.int32),np.diff(self.offsets))

    def graph(self):
        return csr_matrix((np.ones(len(self.targets),np.int8),self.targets,self.offsets),
                          shape=(len(self.bits),len(self.bits)))

    def write_aut(self,path):
        with open(path,'w') as out:
            out.write(f'des (0,{len(self.targets)},{len(self.bits)})\n')
            for s in range(len(self.bits)):
                out.writelines(f'({s},"{self.actions[int(self.labels[e])]}",{self.targets[e]})\n'
                               for e in range(self.offsets[s],self.offsets[s+1]))


def compact_generate(model, observables, dependencies, withdraw=None, omit_sinks=(), max_states=8388608):
    if any(model.max_levels[v] != 1 for v in model.variables):
        raise ValueError('Compact executor requires Boolean nodes')
    if set(omit_sinks) & (set(observables)|set(model.constants)):
        raise ValueError('Cannot omit observable nodes or inputs')
    if any(set(dependencies.get(v,())) & set(omit_sinks) for v in model.variables if v not in omit_sinks):
        raise ValueError('Omitted sink regulates a retained node')
    if withdraw is not None and withdraw not in model.constants:
        raise ValueError('withdrawal requires an input')
    active = tuple(v for v in model.variables if v not in omit_sinks and (v not in model.constants or v==withdraw))
    fixed = tuple((v,value) for v,value in zip(model.variables,model.initial) if v not in active)
    rules = [v for v in active if v not in model.constants]
    counts = np.array([len(dependencies[v]) for v in rules],np.int32)
    width = max(counts,default=0)
    positions = np.full((len(rules),width),-1,np.int32)
    constants = np.zeros_like(positions)
    tables = np.zeros((len(rules),1<<width),np.int8)
    initial_values = dict(zip(model.variables,model.initial))
    actions = ('tau',) + tuple(v+'_'+d for v in observables for d in ('up','down'))
    if withdraw:
        actions += ('withdraw_'+withdraw,)
    visible = np.zeros((len(rules)+1,2),np.int16)
    for r,var in enumerate(rules):
        regs = dependencies[var]
        for j,reg in enumerate(regs):
            if reg in active:
                positions[r,j] = active.index(reg)
            else:
                constants[r,j] = initial_values[reg]
        for code in range(1<<len(regs)):
            values = dict(initial_values)
            values.update({reg:(code>>j)&1 for j,reg in enumerate(regs)})
            tables[r,code] = int(model.rules[var](values))
        if var in observables:
            visible[r] = [actions.index(var+'_down'),actions.index(var+'_up')]
    if withdraw:
        visible[-1,0] = actions.index('withdraw_'+withdraw)
    initial = sum(initial_values[v]<<i for i,v in enumerate(active))
    arrays = _enumerate(initial,len(active),np.array([active.index(v) for v in rules],np.int32),
                        positions,constants,counts,tables,visible,
                        active.index(withdraw) if withdraw else -1,max_states)
    return CompactExecution(model.name,model.variables,active,fixed,*arrays,actions)


@njit(cache=True)
def _propagate(offsets,targets,seeds):
    masks = seeds.copy()
    queue = np.empty(len(seeds)*6,np.int32)
    head,tail = 0,0
    for i in range(len(seeds)):
        if masks[i]:
            queue[tail] = i
            tail += 1
    while head < tail:
        target = queue[head]
        head += 1
        for e in range(offsets[target],offsets[target+1]):
            source = targets[e]
            value = masks[source] | masks[target]
            if value != masks[source]:
                masks[source] = value
                queue[tail] = source
                tail += 1
    return masks


def compact_futures(execution, classify, expanded=True):
    graph = execution.graph()
    n,components = connected_components(graph,directed=True,connection='strong')
    terminal = np.ones(n,bool)
    sources = execution.sources()
    cross = components[sources] != components[execution.targets]
    terminal[components[sources[cross]]] = False
    terminal_states = np.flatnonzero(terminal[components])
    if callable(classify):
        fate_codes = np.array([FATES.index(classify(execution.vector(int(i)))) for i in terminal_states])
    else:
        fate_codes = classify[terminal_states]
    minimum,maximum = np.full(n,99,np.int8),np.full(n,-1,np.int8)
    np.minimum.at(minimum,components[terminal_states],fate_codes)
    np.maximum.at(maximum,components[terminal_states],fate_codes)
    codes = np.where(minimum==maximum,minimum,FATES.index('other'))
    seeds = np.zeros(len(execution.bits),np.uint8)
    seeds[terminal_states] = 1 << codes[components[terminal_states]]
    reverse = graph.transpose().tocsr()
    masks = _propagate(reverse.indptr,reverse.indices,seeds)
    summary = []
    for c in np.flatnonzero(terminal):
        members = terminal_states[components[terminal_states]==c].tolist()
        summary.append({'states':members,'size':len(members),'fate':FATES[codes[c]]})
    result = {'masks':masks,'terminal_components':summary}
    if expanded:
        result['by_state'] = [decode_fates(m) for m in masks]
    return result


def decode_fates(mask):
    return sorted(f for i,f in enumerate(FATES) if int(mask)&(1<<i))


def persistent_states(execution,positive):
    reverse = execution.graph().transpose().tocsr()
    return _propagate(reverse.indptr,reverse.indices,(~positive).astype(np.uint8)) == 0


@njit(cache=True)
def _weak_step(offsets, targets, labels, states, action):
    seen = np.zeros(len(offsets)-1,np.bool_)
    queue = np.empty(len(offsets)-1,np.int32)
    tail = 0
    if action == 0:
        for s in states:
            if not seen[s]:
                seen[s] = True
                queue[tail] = s
                tail += 1
    else:
        for s in states:
            for e in range(offsets[s],offsets[s+1]):
                t = targets[e]
                if labels[e] == action and not seen[t]:
                    seen[t] = True
                    queue[tail] = t
                    tail += 1
    head = 0
    while head < tail:
        s = queue[head]
        head += 1
        for e in range(offsets[s],offsets[s+1]):
            t = targets[e]
            if labels[e] == 0 and not seen[t]:
                seen[t] = True
                queue[tail] = t
                tail += 1
    return np.sort(queue[:tail])


def compact_step(execution, states, action='tau'):
    if action not in execution.actions:
        return np.array([],np.int32)
    return _weak_step(execution.offsets,execution.targets,execution.labels,
                      np.asarray(states,np.int32),execution.actions.index(action))


def compact_trace_check(left,right,max_subsets=10000,max_bytes=250000000,max_seconds=180):
    start_time = time.monotonic()
    alphabet = sorted((set(left.actions)|set(right.actions))-{'tau'})
    start = (compact_step(left,[0]).tobytes(),compact_step(right,[0]).tobytes())
    queue,seen = [(start,())],{start}
    stored_bytes = sum(map(len,start))
    left_only = right_only = None
    complete,reason = True,None
    for (xb,yb),word in queue:
        xs,ys = np.frombuffer(xb,np.int32),np.frombuffer(yb,np.int32)
        if len(xs) and not len(ys) and left_only is None:
            left_only = list(word)
        if len(ys) and not len(xs) and right_only is None:
            right_only = list(word)
        if left_only is not None and right_only is not None:
            complete,reason = False,'both trace inclusions refuted by exact counterexamples'
            break
        for action in alphabet:
            pair = compact_step(left,xs,action).tobytes(),compact_step(right,ys,action).tobytes()
            if pair not in seen:
                if len(seen) >= max_subsets or stored_bytes+sum(map(len,pair)) > max_bytes or time.monotonic()-start_time > max_seconds:
                    complete,reason = False,'subset/time/memory budget exhausted'
                    break
                seen.add(pair)
                stored_bytes += sum(map(len,pair))
                queue.append((pair,word+(action,)))
        if not complete:
            break
    lr = False if left_only is not None else (True if complete else None)
    rl = False if right_only is not None else (True if complete else None)
    return {'status':'disproved' if left_only is not None and right_only is not None else
                    ('complete' if complete else 'inconclusive'),
            'exploration_complete':complete,'reason':reason,
            'algorithm':'exact epsilon-NFA subset-product BFS on compact CSR; no depth cutoff',
            'exact_trace_equal':False if False in (lr,rl) else (True if complete else None),
            'left_trace_included_in_right':lr,'right_trace_included_in_left':rl,
            'left_only_trace':left_only,'right_only_trace':right_only,
            'subset_product_states':len(seen),'stored_subset_bytes':stored_bytes,
            'max_subsets':max_subsets,'max_bytes':max_bytes,'max_seconds':max_seconds}
