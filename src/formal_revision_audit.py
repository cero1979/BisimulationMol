"""R2 audit: independent weak targets, simulation games and exact languages.

The oracle reads only LTS states, edges and initial indices. It does not use
production adjacency, closure, weak-step or relation helpers. Production calls
appear only in comparisons, never in the independent predicates.
"""

from __future__ import annotations

import csv
import itertools
import json
from collections import deque
from pathlib import Path

from . import concurrent_biomodels as cbm
from . import method_benchmark as mb
from . import simulation_oracle as old_oracle

ROOT = Path(__file__).resolve().parents[1]
CONVENTION = "left_simulated_by_right means left <=_w right; right matches left"


class IndependentLTS:
    def __init__(self, lts):
        self.initial = lts.init
        self.n = len(lts.states)
        self.out = [[] for _ in range(self.n)]
        for source, label, target in lts.edges:
            self.out[source].append((label, target))
        self.labels = sorted({label for _, label, _ in lts.edges if label != "tau"})
        self.closure = []
        for source in range(self.n):
            reached, todo = {source}, [source]
            while todo:
                for label, target in self.out[todo.pop()]:
                    if label == "tau" and target not in reached:
                        reached.add(target)
                        todo.append(target)
            self.closure.append(frozenset(reached))
        self.targets = {}
        for source in range(self.n):
            self.targets[source, "tau"] = self.closure[source]
            for label in self.labels:
                self.targets[source, label] = frozenset(
                    end for start in self.closure[source]
                    for action, target in self.out[start] if action == label
                    for end in self.closure[target]
                )

    def replies(self, state, label, weak=True):
        if weak:
            return self.targets.get((state, label), frozenset())
        return frozenset(t for a, t in self.out[state] if a == label)


def game_relation(left, right, *, bisimulation=False, weak=True):
    """Least losing set with simultaneous rounds and explicit failure reasons."""
    a = left if isinstance(left, IndependentLTS) else IndependentLTS(left)
    b = right if isinstance(right, IndependentLTS) else IndependentLTS(right)
    universe = set(itertools.product(range(a.n), range(b.n)))
    losing, certificate = set(), []
    round_number = 0
    while True:
        newly_losing = {}
        for x, y in sorted(universe - losing):
            challenges = [("left", label, target) for label, target in a.out[x]]
            if bisimulation:
                challenges += [("right", label, target) for label, target in b.out[y]]
            for side, label, target in challenges:
                replies = b.replies(y, label, weak) if side == "left" else a.replies(x, label, weak)
                pairs = {(target, z) if side == "left" else (z, target) for z in replies}
                if pairs <= losing:
                    newly_losing[x, y] = {
                        "pair": [x, y], "round": round_number,
                        "attacker_side": side, "label": label, "successor": target,
                        "possible_reply_pairs": [list(p) for p in sorted(pairs)],
                        "reason": "no matching action" if not pairs else "all successor pairs already losing",
                    }
                    break
        if not newly_losing:
            return universe - losing, certificate
        losing.update(newly_losing)
        certificate.extend(newly_losing.values())
        round_number += 1


def independent_predicate(left, right, *, bisimulation=False, weak=True):
    relation, _ = game_relation(left, right, bisimulation=bisimulation, weak=weak)
    return (left.init, right.init) in relation


def verify_candidate_relation(left, right, relation):
    """Check the universal/existential clause on a supplied relation directly."""
    a, b = IndependentLTS(left), IndependentLTS(right)
    violations = []
    for x, y in sorted(relation):
        for label, target in a.out[x]:
            if not any((target, z) in relation for z in b.replies(y, label)):
                violations.append({"pair": [x, y], "label": label, "successor": target})
    return {"valid": not violations, "contains_initial_pair": (left.init, right.init) in relation,
            "violations": violations}


def exact_trace_check(left, right):
    """Exact inclusion both ways by finite epsilon-NFA subset-product search.

    Every original state is accepting (prefix-closed language); the empty subset
    is the sole rejecting state. No trace-depth cutoff is used, including cycles.
    """
    a, b = IndependentLTS(left), IndependentLTS(right)
    start = (a.closure[a.initial], b.closure[b.initial])
    todo, seen = deque([(start, ())]), {start}
    left_only = right_only = None
    alphabet = sorted(set(a.labels) | set(b.labels))
    while todo:
        (xs, ys), word = todo.popleft()
        if xs and not ys and left_only is None:
            left_only = list(word)
        if ys and not xs and right_only is None:
            right_only = list(word)
        for label in alphabet:
            pair = (frozenset(t for x in xs for t in a.replies(x, label)),
                    frozenset(t for y in ys for t in b.replies(y, label)))
            if pair not in seen:
                seen.add(pair)
                todo.append((pair, word + (label,)))
    return {"exact_trace_equal": left_only is None and right_only is None,
            "left_trace_included_in_right": left_only is None,
            "right_trace_included_in_left": right_only is None,
            "left_only_trace": left_only, "right_only_trace": right_only,
            "subset_product_states": len(seen)}


def acyclic_language(lts):
    """Enumerate the complete language, rejecting a cycle rather than truncating."""
    a = IndependentLTS(lts)
    active, memo = set(), {}
    def visit(state):
        if state in active:
            raise ValueError("Exact finite enumeration requires an acyclic reachable graph")
        if state in memo:
            return memo[state]
        active.add(state)
        words = {()}
        for label, target in a.out[state]:
            prefix = () if label == "tau" else (label,)
            words.update(prefix + suffix for suffix in visit(target))
        active.remove(state)
        memo[state] = words
        return words
    return visit(lts.init)


def hierarchy_pairs():
    late, early = mb.branching_time_trap()
    direct = cbm.LTS("a.0", ["p", "q"], 0, [(0, "a", 1)])
    silent = cbm.LTS("a.tau.0", ["p", "r", "q"], 0, [(0, "a", 1), (1, "tau", 2)])
    extra = cbm.LTS("a.(b+c)+a.b", ["x0", "xbc", "xb", "bt", "ct", "bt2"], 0,
                    [(0, "a", 1), (0, "a", 2), (1, "b", 3), (1, "c", 4), (2, "b", 5)])
    return [("weak_not_strong", direct, silent),
            ("mutual_not_bisimilar", extra, late), ("traces_not_mutual", late, early)]


def pair_audit(key, left, right):
    production = {
        "strong_bisimilar": cbm.strong_bisimilar(left, right),
        "weak_bisimilar": cbm.weak_bisimilar(left, right),
        "left_simulated_by_right": cbm.weak_simulates(left, right),
        "right_simulated_by_left": cbm.weak_simulates(right, left),
    }
    independent = {
        "strong_bisimilar": independent_predicate(left, right, bisimulation=True, weak=False),
        "weak_bisimilar": independent_predicate(left, right, bisimulation=True),
        "left_simulated_by_right": independent_predicate(left, right),
        "right_simulated_by_left": independent_predicate(right, left),
    }
    return {"case": key, "left": left.name, "right": right.name,
            "direction_convention": CONVENTION, **production,
            "independent": independent, "independent_oracle_agrees": production == independent,
            **exact_trace_check(left, right)}


def example1_audit():
    late, early = mb.branching_time_trap()
    witness = {(0, 0), (1, 1), (2, 1), (3, 2), (4, 3)}
    el, _ = game_relation(early, late)
    le, failures = game_relation(late, early)
    record = pair_audit("Example 1 (left=late; right=early)", late, early)
    return {**record, "early_simulated_by_late": record["right_simulated_by_left"],
            "late_simulated_by_early": record["left_simulated_by_right"],
            "late_state_names": late.states, "early_state_names": early.states,
            "exact_late_language": [list(w) for w in sorted(acyclic_language(late))],
            "exact_early_language": [list(w) for w in sorted(acyclic_language(early))],
            "candidate_witness_early_to_late": [list(p) for p in sorted(witness)],
            "direct_witness_check": verify_candidate_relation(early, late, witness),
            "surviving_relation_early_to_late": [list(p) for p in sorted(el)],
            "surviving_relation_late_to_early": [list(p) for p in sorted(le)],
            "late_to_early_deletion_certificate": failures,
            "existing_game_agrees": (old_oracle.weak_simulates_game(early, late) == record["right_simulated_by_left"]
                                     and old_oracle.weak_simulates_game(late, early) == record["left_simulated_by_right"])}


def biological_pairs():
    from . import hpn_dream_validation as hpn
    for interface in cbm.GIM_INTERFACE_SPECS:
        animal, plant = cbm.gim_models_for_interface(interface)
        yield "GIM_" + interface, animal.reachability_lts(), plant.reachability_lts()
    for key, spec in cbm.MODULES.items():
        yield key, spec["animal"]().reachability_lts(), spec["plant"]().reachability_lts()
    models = {cell: hpn.model_from_medoid(hpn.select_medoid(cell)) for cell in hpn.CELLS}
    for semantics, builder in [("asynchronous", hpn.asynchronous_lts), ("synchronous", hpn.synchronous_lts)]:
        for condition in hpn.COMMON_CONDITIONS:
            systems = {cell: builder(models[cell], hpn.get_experiment(cell, condition)) for cell in hpn.CELLS}
            for left, right in itertools.combinations(hpn.CELLS, 2):
                yield f"HPN_{semantics}_{condition.name}_{left}_{right}", systems[left], systems[right]


def exhaustive_audit():
    systems = [lts for size in (1, 2) for lts in old_oracle.enumerate_lts(size)]
    prepared = [IndependentLTS(lts) for lts in systems]
    masks, failures, witnesses = [], [], {}
    counts = {"mutual_without_bisimulation": 0, "one_way_with_equal_traces": 0,
              "equal_traces_without_bisimulation": 0}
    weak_count = 0
    for i, left in enumerate(systems):
        mask = 0
        for j, right in enumerate(systems):
            lr = cbm.weak_simulates(left, right)
            rl = cbm.weak_simulates(right, left)
            weak = cbm.weak_bisimilar(left, right)
            strong = cbm.strong_bisimilar(left, right)
            sim_rel, _ = game_relation(prepared[i], prepared[j])
            bi_rel, _ = game_relation(prepared[i], prepared[j], bisimulation=True)
            traces = exact_trace_check(left, right)
            if lr:
                mask |= 1 << j
            weak_count += int(weak)
            checks = [lr == ((left.init, right.init) in sim_rel),
                      weak == ((left.init, right.init) in bi_rel),
                      not strong or weak, not weak or (lr and rl),
                      not lr or traces["left_trace_included_in_right"],
                      not rl or traces["right_trace_included_in_left"]]
            if not all(checks):
                failures.append({"left": left.name, "right": right.name, "checks": checks})
            flags = {"mutual_without_bisimulation": lr and rl and not weak,
                     "one_way_with_equal_traces": (lr != rl) and traces["exact_trace_equal"],
                     "equal_traces_without_bisimulation": traces["exact_trace_equal"] and not weak}
            for name, flag in flags.items():
                if flag:
                    counts[name] += 1
                    witnesses.setdefault(name, {"left": left.name, "right": right.name,
                                                "left_edges": left.edges, "right_edges": right.edges})
        masks.append(mask)
    reflexive = all(mask & (1 << i) for i, mask in enumerate(masks))
    transitive = all(not (mask & (1 << j)) or not (masks[j] & ~mask)
                     for mask in masks for j in range(len(systems)))
    return {"number_of_lts": len(systems), "ordered_lts_pairs": len(systems) ** 2,
            "alphabet": ["a", "tau"], "initial_state": 0,
            "weak_bisimilar_pairs": weak_count, "disagreements_or_hierarchy_failures": failures,
            "simulation_reflexive": reflexive, "simulation_transitive": transitive,
            "all_checks_pass": not failures and reflexive and transitive,
            "search_counts": counts, "first_witnesses": witnesses,
            "scope": "All edge subsets on named one/two-state systems; not all finite systems"}


def write_audits():
    result = ROOT / "results"
    result.mkdir(exist_ok=True)
    def save(name, value):
        (result / name).write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")
    save("example1_simulation_audit.json", example1_audit())
    hierarchy = [pair_audit(*pair) for pair in hierarchy_pairs()]
    save("hierarchy_audit_R2.json", hierarchy)
    records = []
    for case in mb.synthetic_cases():
        row = pair_audit("synthetic_" + case.case, case.reference, case.candidate)
        computed = mb.classify_pair(case.reference, case.candidate)
        row.update(expected_class=case.expected_class, computed_class=computed["formal_class"],
                   expected_class_matches=case.expected_class == computed["formal_class"],
                   trace_distance_k8=computed["trace_distance"])
        records.append(row)
    records.extend(pair_audit(*pair) for pair in biological_pairs())
    save("direction_audit_R2.json", records)
    fields = ["case", "left", "right", "direction_convention", "strong_bisimilar", "weak_bisimilar",
              "left_simulated_by_right", "right_simulated_by_left", "exact_trace_equal", "independent_oracle_agrees"]
    with (result / "direction_audit_R2.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(records)
    assert all(r["independent_oracle_agrees"] for r in records + hierarchy)
    assert all(r.get("expected_class_matches", True) for r in records)
    exhaustive = exhaustive_audit()
    save("exhaustive_formal_audit_R2.json", exhaustive)
    assert exhaustive["all_checks_pass"]
    print(json.dumps({"audited_pairs": len(records), "hierarchy_witnesses": len(hierarchy), **exhaustive}, indent=2))


if __name__ == "__main__":
    write_audits()
