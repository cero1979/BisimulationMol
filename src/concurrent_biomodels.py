"""
concurrent_biomodels.py
=======================

Engine for observational comparison of explicit qualitative biological network
models, with an *Arabidopsis thaliana* versus animal/human illustration. The
engine implements two coupled levels:

  (i)  a biological-computational level that curates *conserved active
       subnetworks* per module, and
  (ii) a formal level that encodes those subnetworks as labelled
       Petri nets and compares their *observable behaviour* under a declared
       observational interface using weak bisimulation, simulation preorders
       and a trace-based behavioural distance.

All returned relations are properties of the supplied models and interface.
They do not establish experimental, kinetic or organism-level equivalence.

The formal core depends only on the Python standard library. Two families of
diagnostic experiments are provided to guard against confirmation bias:

  * ``robustness_under_tau_refinement`` -- checks that verdicts are invariant
    under silent (tau) refinements of a model, i.e. that conclusions do not
    depend on how finely internal steps happen to be drawn; and
  * ``null_baseline_significance`` -- a label-permutation test that quantifies
    how unlikely the observed comparability is under a scrambled interface.

Biological grounding of the curated models:

* D.C. Clavijo-Buritica, C.C. Sosa, R. Cardenas-Heredia, A.J. Mosquera,
  A. Alvarez, J. Medina, M. Quimbaya. "Use of Arabidopsis thaliana as a model
  to understand specific carcinogenic events". Heliyon 9 (2023) e15367.
* M. Quimbaya, K. Vandepoele, E. Raspe, et al. "Identification of putative
  cancer genes through data integration and comparative genomics between plants
  and humans". Cell. Mol. Life Sci. 69 (2012) 2041-2055.

Formal grounding:

* T. Murata. "Petri nets: properties, analysis and applications".
  Proc. IEEE 77(4) (1989) 541-580.
* R. Milner. "Communication and Concurrency". Prentice Hall, 1989.
* D. Sangiorgi. "Introduction to Bisimulation and Coinduction". CUP, 2011.
"""

from __future__ import annotations

import random
from collections import defaultdict, deque
from dataclasses import dataclass, field
from typing import Dict, FrozenSet, Iterable, List, Sequence, Set, Tuple

# Reserved label for internal / unobservable (silent, tau) events.
TAU = "tau"


# ---------------------------------------------------------------------------
# 1. Petri nets (Phase 4: concurrent formalisation)
# ---------------------------------------------------------------------------
@dataclass
class Transition:
    """A transition of a labelled place/transition net.

    pre   : multiset of consumed places (place -> multiplicity).
    post  : multiset of produced places (place -> multiplicity).
    label : observable label of the functional interface, or TAU if internal.
    """

    name: str
    pre: Dict[str, int]
    post: Dict[str, int]
    label: str = TAU


@dataclass
class PetriNet:
    """A labelled place/transition (P/T) net with an initial marking.

    - ``places`` is inferred from the transitions and the initial marking.
    - A marking is represented internally as a tuple of integers aligned with
      ``places`` (stable order) so that it can be used as a state key.
    - The operational semantics is the usual interleaving semantics: at most one
      transition fires per step.
    """

    name: str
    transitions: List[Transition]
    init: Dict[str, int]

    places: Tuple[str, ...] = field(init=False)

    def __post_init__(self) -> None:
        seen: List[str] = []
        for p in self.init:
            if p not in seen:
                seen.append(p)
        for t in self.transitions:
            for p in list(t.pre) + list(t.post):
                if p not in seen:
                    seen.append(p)
        self.places = tuple(seen)

    # -- marking utilities -----------------------------------------------------
    def _marking_tuple(self, marking: Dict[str, int]) -> Tuple[int, ...]:
        return tuple(marking.get(p, 0) for p in self.places)

    def _enabled(self, m: Tuple[int, ...], t: Transition) -> bool:
        idx = {p: i for i, p in enumerate(self.places)}
        return all(m[idx[p]] >= k for p, k in t.pre.items())

    def _fire(self, m: Tuple[int, ...], t: Transition) -> Tuple[int, ...]:
        idx = {p: i for i, p in enumerate(self.places)}
        m2 = list(m)
        for p, k in t.pre.items():
            m2[idx[p]] -= k
        for p, k in t.post.items():
            m2[idx[p]] += k
        return tuple(m2)

    # -- reachability ----------------------------------------------------------
    def _reachable_markings(
        self, max_states: int = 100_000, bound: int = 8
    ) -> Tuple[List[Tuple[int, ...]], Dict[Tuple[int, ...], int], Set[Tuple[int, str, int]]]:
        init = self._marking_tuple(self.init)
        states: List[Tuple[int, ...]] = [init]
        index: Dict[Tuple[int, ...], int] = {init: 0}
        edges: Set[Tuple[int, str, int]] = set()
        stack = [init]
        while stack:
            m = stack.pop()
            for t in self.transitions:
                if self._enabled(m, t):
                    m2 = self._fire(m, t)
                    if any(v > bound for v in m2):
                        raise ValueError(
                            f"Net '{self.name}' is not {bound}-bounded at {t.name}."
                        )
                    if m2 not in index:
                        index[m2] = len(states)
                        states.append(m2)
                        stack.append(m2)
                        if len(states) > max_states:
                            raise ValueError("State explosion: revise the model.")
                    edges.add((index[m], t.label, index[m2]))
        return states, index, edges

    def reachability_lts(self, max_states: int = 100_000, bound: int = 8) -> "LTS":
        """Build the reachability graph as a labelled transition system (LTS).
        Each arc carries the label of the fired transition (observable or TAU).
        ``bound`` caps the number of tokens per place to guarantee finiteness."""
        states, _, edges = self._reachable_markings(max_states, bound)
        return LTS(
            name=self.name,
            states=[repr(s) for s in states],
            init=0,
            edges=sorted(edges),
        )

    def bound(self) -> int:
        """Structural check: maximum number of tokens on any place over all
        reachable markings (1 means the net is *safe* / 1-bounded)."""
        states, _, _ = self._reachable_markings()
        return max((max(m) for m in states), default=0)

    def is_safe(self) -> bool:
        """A net is safe (1-bounded) if no reachable marking exceeds one token
        per place. All curated models in this study are safe by construction."""
        return self.bound() <= 1


# ---------------------------------------------------------------------------
# 2. Labelled transition systems and weak semantics (Phase 5)
# ---------------------------------------------------------------------------
@dataclass
class LTS:
    """A labelled transition system.

    states : list of states (human-readable labels).
    init   : index of the initial state.
    edges  : list of (source, label, target).  TAU = internal event.
    """

    name: str
    states: List[str]
    init: int
    edges: List[Tuple[int, str, int]]

    def __post_init__(self) -> None:
        self._out: Dict[int, List[Tuple[str, int]]] = defaultdict(list)
        for s, a, d in self.edges:
            self._out[s].append((a, d))
        self._tau_cache: Dict[int, FrozenSet[int]] = {}

    @property
    def observables(self) -> Set[str]:
        return {a for _, a, _ in self.edges if a != TAU}

    # -- tau (epsilon) closure -------------------------------------------------
    def tau_closure(self, s: int) -> FrozenSet[int]:
        if s in self._tau_cache:
            return self._tau_cache[s]
        seen = {s}
        stack = [s]
        while stack:
            u = stack.pop()
            for a, v in self._out[u]:
                if a == TAU and v not in seen:
                    seen.add(v)
                    stack.append(v)
        res = frozenset(seen)
        self._tau_cache[s] = res
        return res

    def weak_step(self, s: int, a: str) -> FrozenSet[int]:
        """Weak move  s =a=>  :  tau* . a . tau*   (for a != TAU)."""
        if a == TAU:
            return self.tau_closure(s)
        res: Set[int] = set()
        for s1 in self.tau_closure(s):
            for lab, s2 in self._out[s1]:
                if lab == a:
                    res |= self.tau_closure(s2)
        return frozenset(res)


# ---------------------------------------------------------------------------
# 3. Behavioural equivalences (Phase 5)
# ---------------------------------------------------------------------------
def _obs_labels(l1: LTS, l2: LTS) -> Set[str]:
    return l1.observables | l2.observables


def strong_bisimilar(l1: LTS, l2: LTS) -> bool:
    """Strong bisimulation: TAU is treated as an ordinary label and every step
    must be matched by a single equally labelled step. Used to show that the
    biological comparison needs the *weak* variant (which abstracts internal
    events), not the strong one."""
    R: Set[Tuple[int, int]] = {
        (i, j) for i in range(len(l1.states)) for j in range(len(l2.states))
    }

    def transfer(i: int, j: int, rel: Set[Tuple[int, int]]) -> bool:
        for a, i2 in l1._out[i]:
            if not any(b == a and (i2, j2) in rel for b, j2 in l2._out[j]):
                return False
        for a, j2 in l2._out[j]:
            if not any(b == a and (i2, j2) in rel for b, i2 in l1._out[i]):
                return False
        return True

    changed = True
    while changed:
        changed = False
        for pair in list(R):
            if not transfer(pair[0], pair[1], R):
                R.discard(pair)
                changed = True
    return (l1.init, l2.init) in R


def weak_bisimilar(l1: LTS, l2: LTS) -> bool:
    """True iff the initial states of ``l1`` and ``l2`` are weakly bisimilar
    (Milner). The greatest fixed point over state pairs is computed by
    iterative refinement."""
    R: Set[Tuple[int, int]] = {
        (i, j) for i in range(len(l1.states)) for j in range(len(l2.states))
    }

    def transfer(i: int, j: int, rel: Set[Tuple[int, int]]) -> bool:
        for a, i2 in l1._out[i]:
            targets = l2.tau_closure(j) if a == TAU else l2.weak_step(j, a)
            if not any((i2, t) in rel for t in targets):
                return False
        for a, j2 in l2._out[j]:
            targets = l1.tau_closure(i) if a == TAU else l1.weak_step(i, a)
            if not any((s, j2) in rel for s in targets):
                return False
        return True

    changed = True
    while changed:
        changed = False
        for pair in list(R):
            if not transfer(pair[0], pair[1], R):
                R.discard(pair)
                changed = True
    return (l1.init, l2.init) in R


def weak_simulates(l1: LTS, l2: LTS) -> bool:
    """True iff ``l2`` *weakly simulates* ``l1`` (every move of l1 can be matched
    by l2). We write l1 <= l2, i.e. l1 is a sub-behaviour of l2. One-directional.
    Note: mutual simulation is strictly weaker than bisimulation and is only used
    as a fallback in the verdict rule."""
    R: Set[Tuple[int, int]] = {
        (i, j) for i in range(len(l1.states)) for j in range(len(l2.states))
    }

    def transfer(i: int, j: int, rel: Set[Tuple[int, int]]) -> bool:
        for a, i2 in l1._out[i]:
            targets = l2.tau_closure(j) if a == TAU else l2.weak_step(j, a)
            if not any((i2, t) in rel for t in targets):
                return False
        return True

    changed = True
    while changed:
        changed = False
        for pair in list(R):
            if not transfer(pair[0], pair[1], R):
                R.discard(pair)
                changed = True
    return (l1.init, l2.init) in R


def observable_language(l: LTS, k: int, alphabet: Set[str]) -> Set[Tuple[str, ...]]:
    """Prefix-closed set of weak observable traces of length <= k, where each
    step is a weak move  =a=>  with a in ``alphabet``. This is the *linear-time*
    (trace) semantics used by the behavioural distance."""
    lang: Set[Tuple[str, ...]] = {()}
    start = l.tau_closure(l.init)
    dq: deque = deque((s, ()) for s in start)
    visited: Set[Tuple[int, Tuple[str, ...]]] = {(s, ()) for s in start}
    while dq:
        s, tr = dq.popleft()
        if len(tr) >= k:
            continue
        for a in alphabet:
            for t in l.weak_step(s, a):
                ntr = tr + (a,)
                lang.add(ntr)
                key = (t, ntr)
                if key not in visited:
                    visited.add(key)
                    dq.append((t, ntr))
    return lang


def behavioural_distance(l1: LTS, l2: LTS, k: int = 6) -> float:
    """Trace-based behavioural distance in [0, 1]: the Jaccard distance between
    the weak observable languages truncated at depth ``k``. Equals 0 when both
    systems exhibit the same observable traces up to depth k.

    Relationship to the branching-time verdict (implication chain):
    strong bisimilarity => weak bisimilarity => weak trace equivalence
    => distance 0. The converse does not hold in general (the distance is a
    linear-time index and is coarser than bisimulation), so it is reported as a
    quantitative *complement* to, not a replacement for, the bisimulation
    verdict."""
    alpha = _obs_labels(l1, l2)
    a = observable_language(l1, k, alpha)
    b = observable_language(l2, k, alpha)
    union = a | b
    if not union:
        return 0.0
    return 1.0 - len(a & b) / len(union)


# British/American spelling alias for convenience.
behavioral_distance = behavioural_distance


# ---------------------------------------------------------------------------
# 4. Partial-comparability verdict (Phase 6)
# ---------------------------------------------------------------------------
@dataclass
class Comparison:
    module: str
    hallmark: str
    strong_bisimilar: bool
    weak_bisimilar: bool
    plant_simulated_by_animal: bool  # plant <= animal
    animal_simulated_by_plant: bool  # animal <= plant
    distance: float
    verdict: str
    n_states_animal: int
    n_states_plant: int


def _verdict(bisim: bool, plant_le_animal: bool, animal_le_plant: bool) -> str:
    if bisim:
        return "Comparable (weak bisimulation)"
    if plant_le_animal and animal_le_plant:
        return "Comparable (mutual simulation)"
    if plant_le_animal:
        return "Partial: sub-mechanism simulated (plant \u2291 animal)"
    if animal_le_plant:
        return "Partial: sub-mechanism simulated (animal \u2291 plant)"
    return "Not comparable"


def compare_module(module_key: str, k: int = 6) -> Comparison:
    """Run the full behavioural comparison (Phases 4-6) for one module."""
    spec = MODULES[module_key]
    lts_h = spec["animal"]().reachability_lts()
    lts_a = spec["plant"]().reachability_lts()

    bisim = weak_bisimilar(lts_h, lts_a)
    strong = strong_bisimilar(lts_h, lts_a)
    plant_le_animal = weak_simulates(lts_a, lts_h)  # animal simulates plant
    animal_le_plant = weak_simulates(lts_h, lts_a)  # plant simulates animal
    dist = behavioural_distance(lts_h, lts_a, k=k)

    return Comparison(
        module=module_key,
        hallmark=spec["hallmark"],
        strong_bisimilar=strong,
        weak_bisimilar=bisim,
        plant_simulated_by_animal=plant_le_animal,
        animal_simulated_by_plant=animal_le_plant,
        distance=dist,
        verdict=_verdict(bisim, plant_le_animal, animal_le_plant),
        n_states_animal=len(lts_h.states),
        n_states_plant=len(lts_a.states),
    )


# ---------------------------------------------------------------------------
# 5. Diagnostic experiments (robustness and significance)
# ---------------------------------------------------------------------------
def refine_with_tau(l: LTS, rng: random.Random, n_ins: int) -> LTS:
    """Return a *silent refinement* of ``l``: ``n_ins`` random observable edges
    ``s -a-> d`` are subdivided into ``s -a-> new -tau-> d``. Because inserting a
    silent step preserves the weak-bisimulation class (Milner's tau-law
    tau.P ~ P), a correct method must return the *same* verdict on the refined
    system. This experiment therefore tests robustness to the arbitrary
    granularity with which internal steps are drawn."""
    states = list(l.states)
    edges = list(l.edges)
    for _ in range(n_ins):
        obs = [e for e in edges if e[1] != TAU]
        if not obs:
            break
        s, a, d = rng.choice(obs)
        edges.remove((s, a, d))
        new = len(states)
        states.append(f"ref{new}")
        edges.append((s, a, new))
        edges.append((new, TAU, d))
    return LTS(l.name + "+tau", states, l.init, sorted(set(edges)))


def scramble_labels(l: LTS, rng: random.Random, frac: float) -> LTS:
    """Return a variant of ``l`` in which each observable edge is, independently
    with probability ``frac``, relabelled to a random label drawn from the same
    observable alphabet. Internal (TAU) edges are left untouched. This scrambles
    the biological correspondence encoded by the interface while preserving the
    control-flow skeleton, and is used as the null model for significance."""
    alpha = sorted(l.observables)
    if not alpha:
        return LTS(l.name + "*", list(l.states), l.init, list(l.edges))
    new_edges = []
    for s, a, d in l.edges:
        if a != TAU and rng.random() < frac:
            new_edges.append((s, rng.choice(alpha), d))
        else:
            new_edges.append((s, a, d))
    return LTS(l.name + "*", list(l.states), l.init, sorted(set(new_edges)))


def relabel_observable(l: LTS, old_label: str, new_label: str | None = None) -> LTS:
    """Return an LTS where one observable label is renamed everywhere.

    This is used as a targeted interface-necessity check: if the claimed
    comparability depends on a biologically meaningful read-out, perturbing that
    single read-out on the plant side should increase distance or break the
    relevant equivalence.
    """
    if new_label is None:
        new_label = f"{old_label}__mismatch"
    edges = [
        (s, new_label if a == old_label else a, d)
        for s, a, d in l.edges
    ]
    return LTS(f"{l.name}-{old_label}", list(l.states), l.init, sorted(set(edges)))


def _categorical_verdict(lts_h: LTS, lts_a: LTS, k: int = 6) -> str:
    return _verdict(
        weak_bisimilar(lts_h, lts_a),
        weak_simulates(lts_a, lts_h),
        weak_simulates(lts_h, lts_a),
    )


def robustness_under_tau_refinement(
    module_key: str, n: int = 200, n_ins: int = 3, seed: int = 0
) -> Dict[str, float]:
    """Fraction of ``n`` random silent refinements of the plant model that
    preserve (a) the weak-bisimulation outcome and (b) the categorical verdict.
    A value of 1.0 means the conclusion does not depend on internal granularity.
    """
    spec = MODULES[module_key]
    lts_h = spec["animal"]().reachability_lts()
    lts_a = spec["plant"]().reachability_lts()
    base_bisim = weak_bisimilar(lts_h, lts_a)
    base_verdict = _categorical_verdict(lts_h, lts_a)
    rng = random.Random(seed)
    keep_bisim = keep_verdict = 0
    for _ in range(n):
        ref = refine_with_tau(lts_a, rng, n_ins)
        if weak_bisimilar(lts_h, ref) == base_bisim:
            keep_bisim += 1
        if _categorical_verdict(lts_h, ref) == base_verdict:
            keep_verdict += 1
    return {
        "module": module_key,
        "base_verdict": base_verdict,
        "frac_bisim_preserved": keep_bisim / n,
        "frac_verdict_preserved": keep_verdict / n,
        "n": n,
    }


def null_baseline_significance(
    module_key: str, n: int = 500, frac: float = 0.6, seed: int = 0, k: int = 6
) -> Dict[str, float]:
    """Label-permutation test. Compare the observed behavioural distance between
    animal and plant against the distribution of distances obtained when the
    plant interface is scrambled (``scramble_labels``). Returns the observed
    distance, the null distribution summary and the empirical one-sided p-value
    p = (#{d_scrambled <= d_observed} + 1) / (n + 1)."""
    spec = MODULES[module_key]
    lts_h = spec["animal"]().reachability_lts()
    lts_a = spec["plant"]().reachability_lts()
    d0 = behavioural_distance(lts_h, lts_a, k=k)
    rng = random.Random(seed)
    null = []
    le = 0
    for _ in range(n):
        sc = scramble_labels(lts_a, rng, frac)
        d = behavioural_distance(lts_h, sc, k=k)
        null.append(d)
        if d <= d0 + 1e-12:
            le += 1
    mean = sum(null) / n
    var = sum((d - mean) ** 2 for d in null) / n
    return {
        "module": module_key,
        "observed_distance": d0,
        "null_mean": mean,
        "null_sd": var ** 0.5,
        "p_value": (le + 1) / (n + 1),
        "null": null,
    }


def benjamini_hochberg(p_values: Sequence[float]) -> List[float]:
    """Benjamini-Hochberg false-discovery-rate correction.

    The null-baseline experiment tests one hypothesis per module. Reporting raw
    empirical p-values alone is optimistic, so the manuscript and notebook use
    these q-values for the hostile-reviewer version of the statistical claim.
    """
    m = len(p_values)
    if m == 0:
        return []
    order = sorted(range(m), key=lambda i: p_values[i])
    q = [1.0] * m
    running = 1.0
    for rank, idx in reversed(list(enumerate(order, start=1))):
        running = min(running, p_values[idx] * m / rank)
        q[idx] = min(running, 1.0)
    return q


def null_baseline_suite(
    modules: Iterable[str] | None = None,
    n: int = 500,
    frac: float = 0.6,
    seed: int = 0,
    k: int = 6,
) -> List[Dict[str, float]]:
    """Run the label-permutation null test for several modules and attach
    Benjamini-Hochberg q-values across the family of tests."""
    mods = list(MODULES if modules is None else modules)
    rows = [
        null_baseline_significance(m, n=n, frac=frac, seed=seed, k=k)
        for m in mods
    ]
    q_values = benjamini_hochberg([float(r["p_value"]) for r in rows])
    for row, q in zip(rows, q_values):
        row["q_value_bh"] = q
    return rows


def interface_necessity(module_key: str, k: int = 6) -> List[Dict[str, object]]:
    """Targeted label-necessity stress test.

    For each plant observable label, rename that label only in the plant LTS and
    recompute the comparison against the unmodified animal LTS. The output shows
    which interface labels are doing real discriminative work, rather than being
    inert decoration. Labels absent from the common interface are still tested
    because they explain non-comparability in controls.
    """
    spec = MODULES[module_key]
    lts_h = spec["animal"]().reachability_lts()
    lts_a = spec["plant"]().reachability_lts()
    base = {
        "weak_bisimilar": weak_bisimilar(lts_h, lts_a),
        "plant_simulated_by_animal": weak_simulates(lts_a, lts_h),
        "animal_simulated_by_plant": weak_simulates(lts_h, lts_a),
        "distance": behavioural_distance(lts_h, lts_a, k=k),
        "verdict": _categorical_verdict(lts_h, lts_a, k=k),
    }
    rows: List[Dict[str, object]] = []
    for label in sorted(lts_a.observables):
        perturbed = relabel_observable(lts_a, label)
        verdict = _categorical_verdict(lts_h, perturbed, k=k)
        dist = behavioural_distance(lts_h, perturbed, k=k)
        rows.append(
            {
                "module": module_key,
                "label": label,
                "base_verdict": base["verdict"],
                "base_distance": base["distance"],
                "perturbed_verdict": verdict,
                "perturbed_distance": dist,
                "delta_distance": dist - float(base["distance"]),
                "weak_bisimilar_after": weak_bisimilar(lts_h, perturbed),
                "verdict_changed": verdict != base["verdict"],
            }
        )
    return rows


def null_seed_sensitivity(
    modules: Iterable[str] | None = None,
    seeds: Sequence[int] = (1, 7, 13, 29, 101),
    n: int = 2000,
    frac: float = 0.6,
    k: int = 6,
) -> List[Dict[str, object]]:
    """Repeat the null-baseline suite across seeds and summarise q-value ranges."""
    mods = list(MODULES if modules is None else modules)
    by_module: Dict[str, List[float]] = {m: [] for m in mods}
    p_by_module: Dict[str, List[float]] = {m: [] for m in mods}
    for seed in seeds:
        rows = null_baseline_suite(mods, n=n, frac=frac, seed=seed, k=k)
        for row in rows:
            by_module[row["module"]].append(float(row["q_value_bh"]))
            p_by_module[row["module"]].append(float(row["p_value"]))
    return [
        {
            "module": m,
            "seeds": ",".join(str(s) for s in seeds),
            "n_per_seed": n,
            "q_min": min(by_module[m]),
            "q_median": sorted(by_module[m])[len(by_module[m]) // 2],
            "q_max": max(by_module[m]),
            "p_min": min(p_by_module[m]),
            "p_median": sorted(p_by_module[m])[len(p_by_module[m]) // 2],
            "p_max": max(p_by_module[m]),
            "all_q_lt_0_05": all(q < 0.05 for q in by_module[m]),
        }
        for m in mods
    ]


def distance_curve(module_key: str, kmax: int = 12) -> List[Tuple[int, float]]:
    """Behavioural distance as a function of the trace-truncation depth k.
    For acyclic modules the observable language is finite, so the distance is
    exact once k reaches the module diameter."""
    spec = MODULES[module_key]
    lts_h = spec["animal"]().reachability_lts()
    lts_a = spec["plant"]().reachability_lts()
    return [(k, behavioural_distance(lts_h, lts_a, k=k)) for k in range(1, kmax + 1)]


# ===========================================================================
# 6. CURATED BIOLOGICAL MODELS (Phases 1-4)
# ===========================================================================
# The case-study registry below contributes two Petri nets (animal/human and
# Arabidopsis) per cancer-relevant module over a common observational interface.
# The formal API itself is organism-agnostic: compare_pair() accepts any two
# module builders. Places encode molecular states, transitions encode
# regulatory/biochemical events and tokens encode activation. The exact
# literature statement behind every case-study transition is recorded in
# MODEL_PROVENANCE below so that the construction is auditable and reproducible.

# --- Module GIM: DNA damage response and repair ----------------------------
def ddr_animal() -> PetriNet:
    """DNA damage response (mammal). ATM senses DSB, ATR senses SSB; CHK2/CHK1
    -> p53 -> p21 -| CDK (arrest). Repair (HR/NHEJ, BER/NER). Severe irreparable
    damage -> apoptosis (exit from the proliferative pool)."""
    T = [
        Transition("sense_DSB", {"stress": 1}, {"dsb": 1, "atm": 1}, "damage"),
        Transition("sense_SSB", {"stress": 1}, {"ssb": 1, "atr": 1}, "damage"),
        Transition("ATM_CHK2", {"atm": 1}, {"chk": 1}, TAU),
        Transition("ATR_CHK1", {"atr": 1}, {"chk": 1}, TAU),
        Transition("CHK_p53", {"chk": 1}, {"p53": 1}, TAU),
        Transition("p53_p21_arrest", {"p53": 1}, {"arrest": 1}, "checkpoint"),
        Transition("repair_HR_NHEJ", {"arrest": 1, "dsb": 1}, {"repairing": 1}, "repair"),
        Transition("repair_BER_NER", {"arrest": 1, "ssb": 1}, {"repairing": 1}, "repair"),
        Transition("repair_ok", {"repairing": 1}, {"restored": 1}, "restored"),
        Transition("repair_fail", {"repairing": 1}, {"severe": 1}, TAU),
        Transition("apoptosis", {"severe": 1}, {"dead": 1}, "exit_cycle"),
    ]
    return PetriNet("GIM_animal", T, {"stress": 1})


def ddr_plant() -> PetriNet:
    """DNA damage response (Arabidopsis). ATM/ATR signal through the
    plant-specific SOG1 programme; WEE1 and SMR proteins inhibit cell-cycle
    progression. The minimal net encodes an SMR-associated, combined
    differentiation/endoreduplication terminal outcome and does not claim to
    represent every tissue-dependent plant damage response."""
    T = [
        Transition("sense_DSB", {"stress": 1}, {"dsb": 1, "atm": 1}, "damage"),
        Transition("sense_SSB", {"stress": 1}, {"ssb": 1, "atr": 1}, "damage"),
        Transition("ATM_sig", {"atm": 1}, {"chk": 1}, TAU),
        Transition("ATR_sig", {"atr": 1}, {"chk": 1}, TAU),
        Transition("SOG1_program", {"chk": 1}, {"trans": 1}, TAU),
        Transition("WEE1_arrest", {"trans": 1}, {"arrest": 1}, "checkpoint"),
        Transition("repair_HR_NHEJ", {"arrest": 1, "dsb": 1}, {"repairing": 1}, "repair"),
        Transition("repair_BER_NER", {"arrest": 1, "ssb": 1}, {"repairing": 1}, "repair"),
        Transition("repair_ok", {"repairing": 1}, {"restored": 1}, "restored"),
        Transition("repair_fail", {"repairing": 1}, {"severe": 1}, TAU),
        Transition("SMR_induction", {"severe": 1}, {"smr": 1}, TAU),
        Transition("differentiation", {"smr": 1}, {"differentiated": 1}, "exit_cycle"),
    ]
    return PetriNet("GIM_plant", T, {"stress": 1})


# The three interfaces below are biological hypotheses fixed independently of
# their formal outcomes.  They expose progressively more of the same two GIM
# nets; no places, arcs, transitions, or initial markings are changed.
GIM_INTERFACE_SPECS: Dict[str, Dict[str, object]] = {
    "A": {
        "name": "coarse functional/process",
        "biological_question": (
            "Do the encoded models preserve a shared high-level damage-response "
            "control structure when organism-specific implementation is hidden?"
        ),
        "rationale": (
            "Damage detection, checkpoint activation, repair, restoration, and "
            "loss of proliferative capacity are observed as functional processes."
        ),
        "literature_keys": (
            "JacksonBartek2009;Yoshiyama2013;DeSchutter2007;Adachi2011;"
            "FulcherSablowski2009"
        ),
        "animal_labels": {
            "sense_DSB": "damage_detection",
            "sense_SSB": "damage_detection",
            "p53_p21_arrest": "checkpoint_activation",
            "repair_HR_NHEJ": "repair",
            "repair_BER_NER": "repair",
            "repair_ok": "restoration",
            "apoptosis": "cell_cycle_exit",
        },
        "plant_labels": {
            "sense_DSB": "damage_detection",
            "sense_SSB": "damage_detection",
            "WEE1_arrest": "checkpoint_activation",
            "repair_HR_NHEJ": "repair",
            "repair_BER_NER": "repair",
            "repair_ok": "restoration",
            "differentiation": "cell_cycle_exit",
        },
    },
    "B": {
        "name": "intermediate pathway",
        "biological_question": (
            "Does the relation persist when damage channel, ATM/ATR signalling, "
            "and repair family are distinguished but terminal fate is collapsed?"
        ),
        "rationale": (
            "The interface separates DSB-associated and replication-stress "
            "channels and broad repair families while retaining a common "
            "functional checkpoint and cell-cycle-exit readout."
        ),
        "literature_keys": (
            "BlackfordJackson2017;Yoshiyama2013;DeSchutter2007;Ogita2018;"
            "ManovaGruszka2015"
        ),
        "animal_labels": {
            "sense_DSB": "dsb_detection",
            "sense_SSB": "replication_stress_detection",
            "ATM_CHK2": "atm_pathway_signal",
            "ATR_CHK1": "atr_pathway_signal",
            "p53_p21_arrest": "checkpoint_activation",
            "repair_HR_NHEJ": "dsb_repair",
            "repair_BER_NER": "excision_repair",
            "repair_ok": "restoration",
            "apoptosis": "cell_cycle_exit",
        },
        "plant_labels": {
            "sense_DSB": "dsb_detection",
            "sense_SSB": "replication_stress_detection",
            "ATM_sig": "atm_pathway_signal",
            "ATR_sig": "atr_pathway_signal",
            "WEE1_arrest": "checkpoint_activation",
            "repair_HR_NHEJ": "dsb_repair",
            "repair_BER_NER": "excision_repair",
            "repair_ok": "restoration",
            "differentiation": "cell_cycle_exit",
        },
    },
    "C": {
        "name": "mechanism-resolved terminal fate",
        "biological_question": (
            "Do the encoded models remain behaviorally related when their "
            "organism-specific terminal mechanisms are observable?"
        ),
        "rationale": (
            "This interface retains the intermediate pathway distinctions and "
            "separates mammalian apoptosis from plant SMR induction and the "
            "model's combined differentiation/endoreduplication outcome."
        ),
        "literature_keys": (
            "JacksonBartek2009;Yi2014;Adachi2011;FulcherSablowski2009;Ogita2018"
        ),
        "animal_labels": {
            "sense_DSB": "dsb_detection",
            "sense_SSB": "replication_stress_detection",
            "ATM_CHK2": "atm_pathway_signal",
            "ATR_CHK1": "atr_pathway_signal",
            "p53_p21_arrest": "checkpoint_activation",
            "repair_HR_NHEJ": "dsb_repair",
            "repair_BER_NER": "excision_repair",
            "repair_ok": "restoration",
            "apoptosis": "apoptosis",
        },
        "plant_labels": {
            "sense_DSB": "dsb_detection",
            "sense_SSB": "replication_stress_detection",
            "ATM_sig": "atm_pathway_signal",
            "ATR_sig": "atr_pathway_signal",
            "WEE1_arrest": "checkpoint_activation",
            "repair_HR_NHEJ": "dsb_repair",
            "repair_BER_NER": "excision_repair",
            "repair_ok": "restoration",
            "SMR_induction": "smr_induction",
            "differentiation": "differentiation_or_endoreduplication",
        },
    },
}


GIM_INTERFACE_JUSTIFICATION: List[Dict[str, str]] = [
    {
        "event_process": "Damage sensing",
        "animal_human_interpretation": (
            "ATM-dominant DSB signalling and ATR-dominant replication-stress/ssDNA signalling"
        ),
        "arabidopsis_interpretation": (
            "ATM and ATR initiate lesion- and replication-stress responses upstream of SOG1"
        ),
        "interface_status": (
            "A: one observable damage_detection label; B/C: DSB and replication-stress labels"
        ),
        "biological_reason": (
            "Detection is a shared function, while B/C retain the biologically relevant initiating channel."
        ),
        "literature_support": "BlackfordJackson2017;Yoshiyama2013;Adachi2011",
    },
    {
        "event_process": "Checkpoint signalling and arrest",
        "animal_human_interpretation": "CHK1/CHK2-p53-p21 control of cyclin-dependent kinases",
        "arabidopsis_interpretation": "SOG1-regulated WEE1 and SMR checkpoint control",
        "interface_status": (
            "A: checkpoint observable, relays internal; B/C: ATM/ATR channels and checkpoint observable"
        ),
        "biological_reason": (
            "The arrest function is comparable without treating p53 and SOG1 as orthologous mechanisms."
        ),
        "literature_support": "JacksonBartek2009;DeSchutter2007;Yi2014;Ogita2018",
    },
    {
        "event_process": "DNA repair and recovery",
        "animal_human_interpretation": "DSB repair and excision-repair families followed by recovery",
        "arabidopsis_interpretation": "Conserved broad repair families followed by recovery",
        "interface_status": (
            "A: repair/restoration observables; B/C: DSB repair, excision repair, and restoration"
        ),
        "biological_reason": (
            "Broad repair functions are conserved, but the qualitative nets do not encode pathway kinetics or fidelity."
        ),
        "literature_support": "JacksonBartek2009;ManovaGruszka2015;Yoshiyama2013",
    },
    {
        "event_process": "Terminal response to unresolved damage",
        "animal_human_interpretation": "Apoptotic removal from the proliferative pool",
        "arabidopsis_interpretation": (
            "SMR-associated arrest followed by a combined differentiation/endoreduplication model outcome"
        ),
        "interface_status": (
            "A/B: common cell_cycle_exit observable; C: apoptosis, SMR induction, and plant outcome separated"
        ),
        "biological_reason": (
            "A/B ask about loss of proliferative capacity; C tests mechanism-specific readouts. "
            "The plant model does not resolve differentiation and endoreduplication as separate branches."
        ),
        "literature_support": "JacksonBartek2009;Yi2014;Adachi2011;FulcherSablowski2009",
    },
]


def relabel_net_by_transition(
    net: PetriNet, transition_labels: Dict[str, str], name: str | None = None
) -> PetriNet:
    """Clone a net while declaring observables by transition name.

    Transitions omitted from ``transition_labels`` become internal.  Rejecting
    unknown names prevents a misspelled biological interface from silently
    changing an analysis.
    """
    names = {transition.name for transition in net.transitions}
    unknown = set(transition_labels) - names
    if unknown:
        raise ValueError(f"Unknown transitions for {net.name}: {sorted(unknown)}")
    transitions = [
        Transition(
            transition.name,
            dict(transition.pre),
            dict(transition.post),
            transition_labels.get(transition.name, TAU),
        )
        for transition in net.transitions
    ]
    return PetriNet(name or net.name, transitions, dict(net.init))


def gim_models_for_interface(interface_id: str) -> Tuple[PetriNet, PetriNet]:
    """Return the unchanged GIM structures relabelled for interface A, B, or C."""
    try:
        specification = GIM_INTERFACE_SPECS[interface_id]
    except KeyError as exc:
        raise ValueError(f"Unknown GIM interface: {interface_id}") from exc
    animal = relabel_net_by_transition(
        ddr_animal(),
        specification["animal_labels"],  # type: ignore[arg-type]
        f"GIM_animal_interface_{interface_id}",
    )
    plant = relabel_net_by_transition(
        ddr_plant(),
        specification["plant_labels"],  # type: ignore[arg-type]
        f"GIM_plant_interface_{interface_id}",
    )
    return animal, plant


# --- Module DCE: deregulating cellular energetics ---------------------------
def energy_animal() -> PetriNet:
    """Central energy metabolism (human): glycolysis -> pyruvate ->
    (aerobic respiration TCA/OXPHOS) or (lactic fermentation, LDH: Warburg).
    Both routes yield ATP."""
    T = [
        Transition("glucose_uptake", {"glucose": 1}, {"g6p": 1}, "uptake"),
        Transition("glycolysis", {"g6p": 1}, {"pyruvate": 1}, "glycolysis"),
        Transition("respiration", {"pyruvate": 1}, {"tca": 1}, "branch_resp"),
        Transition("oxphos", {"tca": 1}, {"atp": 1}, "atp"),
        Transition("fermentation_LDH", {"pyruvate": 1}, {"lactate": 1}, "reprogram"),
        Transition("warburg_atp", {"lactate": 1}, {"atp": 1}, "atp"),
    ]
    return PetriNet("DCE_animal", T, {"glucose": 1})


def energy_plant() -> PetriNet:
    """Central energy metabolism (Arabidopsis): conserved glycolysis, TCA,
    fermentation and LDH machinery. An internal buffer (tau) represents the
    chloroplastic/redox integration preceding glycolysis."""
    T = [
        Transition("glucose_uptake", {"glucose": 1}, {"g6p": 1}, "uptake"),
        Transition("redox_buffer", {"g6p": 1}, {"g6p2": 1}, TAU),
        Transition("glycolysis", {"g6p2": 1}, {"pyruvate": 1}, "glycolysis"),
        Transition("respiration", {"pyruvate": 1}, {"tca": 1}, "branch_resp"),
        Transition("oxphos", {"tca": 1}, {"atp": 1}, "atp"),
        Transition("fermentation_LDH", {"pyruvate": 1}, {"lactate": 1}, "reprogram"),
        Transition("warburg_atp", {"lactate": 1}, {"atp": 1}, "atp"),
    ]
    return PetriNet("DCE_plant", T, {"glucose": 1})


# --- Module SPS/ERI: cell cycle / sustained proliferation -------------------
def cellcycle_animal() -> PetriNet:
    """Cell cycle (human): mitogens -> RB-E2F pathway (G1-S) -> origin licensing
    (ORC/MCM) -> S phase -> G2-M -> division (return to quiescence)."""
    T = [
        Transition("mitogen", {"quiescent": 1}, {"rb_e2f": 1}, "mitogen"),
        Transition("RB_E2F_G1S", {"rb_e2f": 1}, {"origins": 1}, "g1s"),
        Transition("ORC_MCM_licensing", {"origins": 1}, {"prerc": 1}, "licensing"),
        Transition("S_phase", {"prerc": 1}, {"replicated": 1}, "sphase"),
        Transition("G2M", {"replicated": 1}, {"mitosis": 1}, "g2m"),
        Transition("division", {"mitosis": 1}, {"quiescent": 1}, "division"),
    ]
    return PetriNet("SPS_animal", T, {"quiescent": 1})


def cellcycle_plant() -> PetriNet:
    """Cell cycle (Arabidopsis): conserved RB-E2F pathway and ORC/MCM complexes
    (Quimbaya et al. 2012: ETG1/MCMBP). An internal adjustment (tau) represents
    plant-specific restriction-point regulation."""
    T = [
        Transition("mitogen", {"quiescent": 1}, {"rb_e2f": 1}, "mitogen"),
        Transition("restriction_tune", {"rb_e2f": 1}, {"rb_e2f2": 1}, TAU),
        Transition("RB_E2F_G1S", {"rb_e2f2": 1}, {"origins": 1}, "g1s"),
        Transition("ORC_MCM_licensing", {"origins": 1}, {"prerc": 1}, "licensing"),
        Transition("S_phase", {"prerc": 1}, {"replicated": 1}, "sphase"),
        Transition("G2M", {"replicated": 1}, {"mitosis": 1}, "g2m"),
        Transition("division", {"mitosis": 1}, {"quiescent": 1}, "division"),
    ]
    return PetriNet("SPS_plant", T, {"quiescent": 1})


def cellcycle_mouse() -> PetriNet:
    """Cell cycle (Mus musculus). The mammalian control circuit is essentially
    the human one (RB-E2F, ORC/MCM licensing, G2-M), so the model shares the
    human structure. It is used in the cross-organism demonstration to show that
    the method rates a phylogenetically close model as maximally comparable
    (strong bisimulation)."""
    T = [
        Transition("mitogen", {"quiescent": 1}, {"rb_e2f": 1}, "mitogen"),
        Transition("RB_E2F_G1S", {"rb_e2f": 1}, {"origins": 1}, "g1s"),
        Transition("ORC_MCM_licensing", {"origins": 1}, {"prerc": 1}, "licensing"),
        Transition("S_phase", {"prerc": 1}, {"replicated": 1}, "sphase"),
        Transition("G2M", {"replicated": 1}, {"mitosis": 1}, "g2m"),
        Transition("division", {"mitosis": 1}, {"quiescent": 1}, "division"),
    ]
    return PetriNet("SPS_mouse", T, {"quiescent": 1})


def cellcycle_yeast() -> PetriNet:
    """Cell cycle (Saccharomyces cerevisiae). The conserved eukaryotic core
    (START/G1-S; ORC/MCM origin licensing -- first described in yeast; S phase;
    B-cyclin/CDK-driven G2-M; division) with yeast-specific internal regulation
    (SBF/MBF transcriptional activation; Clb-CDK with the Swe1/Mih1 analogues of
    Wee1/Cdc25) modelled as tau steps. Weakly, but not strongly, bisimilar to the
    human reference."""
    T = [
        Transition("mitogen", {"quiescent": 1}, {"cln": 1}, "mitogen"),
        Transition("SBF_MBF", {"cln": 1}, {"sbf": 1}, TAU),
        Transition("START_G1S", {"sbf": 1}, {"origins": 1}, "g1s"),
        Transition("ORC_MCM_licensing", {"origins": 1}, {"prerc": 1}, "licensing"),
        Transition("S_phase", {"prerc": 1}, {"replicated": 1}, "sphase"),
        Transition("Clb_CDK", {"replicated": 1}, {"clb": 1}, TAU),
        Transition("G2M", {"clb": 1}, {"mitosis": 1}, "g2m"),
        Transition("division", {"mitosis": 1}, {"quiescent": 1}, "division"),
    ]
    return PetriNet("SPS_yeast", T, {"quiescent": 1})


def cellcycle_scrambled_control() -> PetriNet:
    """Negative portability control for the cell-cycle demonstration.

    The control reuses the same observable alphabet as the conserved cell-cycle
    models but puts the read-outs in a biologically incoherent order. A general
    method should reject this model despite its superficially matching labels.
    """
    T = [
        Transition("division_first", {"quiescent": 1}, {"mitosis": 1}, "division"),
        Transition("reverse_G2M", {"mitosis": 1}, {"replicated": 1}, "g2m"),
        Transition("reverse_S", {"replicated": 1}, {"prerc": 1}, "sphase"),
        Transition("reverse_license", {"prerc": 1}, {"origins": 1}, "licensing"),
        Transition("reverse_G1S", {"origins": 1}, {"rb_e2f": 1}, "g1s"),
        Transition("mitogen_last", {"rb_e2f": 1}, {"quiescent": 1}, "mitogen"),
    ]
    return PetriNet("SPS_scrambled_control", T, {"quiescent": 1})


# --- Module RCD: programmed cell death and autophagy ------------------------
def death_animal() -> PetriNet:
    """Cell death / autophagy (animal): stress/ROS -> mTOR inhibition ->
    autophagy; autophagy may promote survival or commit to death; the canonical
    execution is caspase-dependent apoptosis."""
    T = [
        Transition("stress_ROS", {"cell": 1}, {"ros": 1}, "stress"),
        Transition("mTOR_off", {"ros": 1}, {"mtor_low": 1}, "mtor_off"),
        Transition("autophagy", {"mtor_low": 1}, {"autoph": 1}, "autophagy"),
        Transition("survive", {"autoph": 1}, {"survivor": 1}, "survive"),
        Transition("commit_PCD", {"autoph": 1}, {"apop": 1}, "pcd_commit"),
        Transition("caspase_execution", {"apop": 1}, {"dead": 1}, "apoptosis"),
    ]
    return PetriNet("RCD_animal", T, {"cell": 1})


def death_plant() -> PetriNet:
    """Cell death / autophagy (Arabidopsis): conserved autophagy (SnRK1/TOR, ATG
    genes). Plant PCD uses metacaspases and shares only some apoptotic hallmarks:
    the canonical caspase-dependent execution is NOT conserved (terminal
    execution is an internal, tau, event)."""
    T = [
        Transition("stress_ROS", {"cell": 1}, {"ros": 1}, "stress"),
        Transition("mTOR_off", {"ros": 1}, {"mtor_low": 1}, "mtor_off"),
        Transition("autophagy", {"mtor_low": 1}, {"autoph": 1}, "autophagy"),
        Transition("survive", {"autoph": 1}, {"survivor": 1}, "survive"),
        Transition("commit_PCD", {"autoph": 1}, {"mcd": 1}, "pcd_commit"),
        Transition("metacaspase_exec", {"mcd": 1}, {"dead": 1}, TAU),
    ]
    return PetriNet("RCD_plant", T, {"cell": 1})


# --- Module AID: avoiding immune destruction (negative control) -------------
def immune_animal() -> PetriNet:
    """Immune system (animal): innate immunity (PRR/TLR -> MAPK -> effectors)
    AND adaptive immunity (clonal selection, immunological memory), absent in
    plants."""
    T = [
        Transition("recognition", {"pathogen": 1}, {"prr": 1}, "recognition"),
        Transition("innate_MAPK", {"prr": 1}, {"mapk": 1}, "innate_signal"),
        Transition("effectors", {"mapk": 1}, {"defense": 1}, "effector"),
        Transition("clonal_selection", {"prr": 1}, {"lymph": 1}, "clonal_selection"),
        Transition("immune_memory", {"lymph": 1}, {"memory": 1}, "memory"),
    ]
    return PetriNet("AID_animal", T, {"pathogen": 1})


def immune_plant() -> PetriNet:
    """Immune system (Arabidopsis): innate immunity (PRR/RLK, NLR) and a
    plant-specific response (cell-wall reinforcement / SAR) with no animal
    counterpart. Lacks adaptive immunity (clonal selection, lymphocyte
    memory)."""
    T = [
        Transition("recognition", {"pathogen": 1}, {"prr": 1}, "recognition"),
        Transition("innate_MAPK", {"prr": 1}, {"mapk": 1}, "innate_signal"),
        Transition("effectors", {"mapk": 1}, {"defense": 1}, "effector"),
        Transition("cell_wall_SAR", {"prr": 1}, {"wall": 1}, "cell_wall"),
    ]
    return PetriNet("AID_plant", T, {"pathogen": 1})


# --- Module registry --------------------------------------------------------
MODULES: Dict[str, dict] = {
    "GIM": {
        "hallmark": "Genome Instability & Mutation (DNA repair)",
        "user_module": "DNA repair and genome instability",
        "animal": ddr_animal,
        "plant": ddr_plant,
    },
    "DCE": {
        "hallmark": "Deregulating Cellular Energetics (metabolism)",
        "user_module": "Central energy metabolism",
        "animal": energy_animal,
        "plant": energy_plant,
    },
    "SPS": {
        "hallmark": "Sustaining Proliferative Signaling / Replicative Immortality",
        "user_module": "Cell-cycle regulation",
        "animal": cellcycle_animal,
        "plant": cellcycle_plant,
    },
    "RCD": {
        "hallmark": "Resisting Cell Death (cell death / autophagy)",
        "user_module": "Programmed cell death and autophagy",
        "animal": death_animal,
        "plant": death_plant,
    },
    "AID": {
        "hallmark": "Avoiding Immune Destruction (negative control)",
        "user_module": "Immune evasion (not prioritised)",
        "animal": immune_animal,
        "plant": immune_plant,
    },
}


# --- Model provenance: literature statement behind each transition ----------
# (transition, biological event modelled, evidence tag). Evidence tags:
#   CB2023 = Clavijo-Buritica et al. (2023);  Q2012 = Quimbaya et al. (2012).
MODEL_PROVENANCE: Dict[str, List[Tuple[str, str, str]]] = {
    "GIM": [
        ("sense_DSB", "ATM-associated double-strand-break signalling",
         "JacksonBartek2009, BlackfordJackson2017, Yoshiyama2013"),
        ("sense_SSB", "ATR-associated ssDNA/replication-stress signalling",
         "BlackfordJackson2017, Yoshiyama2013"),
        ("ATM_CHK2 / ATR_CHK1 / ATM_sig / ATR_sig / SOG1_program",
         "animal checkpoint relays and the plant-specific SOG1 programme",
         "BlackfordJackson2017, Adachi2011, Ogita2018"),
        ("CHK_p53 / p53_p21_arrest / WEE1_arrest",
         "cell-cycle arrest (p53-p21-CDK / SOG1-WEE1)",
         "JacksonBartek2009, DeSchutter2007, Ogita2018"),
        ("repair_HR_NHEJ / repair_BER_NER", "broad DSB and excision-repair families",
         "JacksonBartek2009, ManovaGruszka2015"),
        ("repair_ok / repair_fail", "encoded recovery or unresolved-damage branch",
         "JacksonBartek2009, Yoshiyama2013"),
        ("apoptosis (animal)", "encoded apoptotic loss from the proliferative pool",
         "JacksonBartek2009"),
        ("SMR_induction + differentiation (plant)",
         "SMR-associated arrest and a combined differentiation/endoreduplication outcome",
         "Yi2014, Adachi2011, FulcherSablowski2009"),
    ],
    "DCE": [
        ("glucose_uptake / glycolysis", "conserved glycolysis", "CB2023"),
        ("respiration / oxphos", "TCA cycle and oxidative phosphorylation", "CB2023"),
        ("fermentation_LDH / warburg_atp",
         "lactate dehydrogenase present in both species (Warburg-like)", "CB2023"),
        ("redox_buffer (plant)", "chloroplastic/redox integration (internal)", "CB2023"),
    ],
    "SPS": [
        ("mitogen / RB_E2F_G1S", "conserved RB-E2F control of G1-S", "CB2023"),
        ("ORC_MCM_licensing", "conserved ORC/MCM origin licensing", "CB2023, Q2012"),
        ("S_phase / G2M / division", "replication and division", "CB2023"),
        ("restriction_tune (plant)", "plant restriction-point tuning (internal)", "Q2012"),
    ],
    "RCD": [
        ("stress_ROS / mTOR_off", "ROS-driven TOR inhibition", "CB2023"),
        ("autophagy", "conserved autophagy (TOR-SnRK1, ATG genes)", "CB2023"),
        ("survive / commit_PCD", "survival branch or commitment to programmed cell death", "CB2023"),
        ("caspase_execution (animal)", "canonical caspase-dependent apoptosis", "CB2023"),
        ("metacaspase_exec (plant)",
         "metacaspase execution; no canonical caspase observable", "CB2023"),
    ],
    "AID": [
        ("recognition / innate_MAPK / effectors", "conserved innate immunity (convergent)", "CB2023"),
        ("clonal_selection / immune_memory (animal)", "adaptive immunity (absent in plants)", "CB2023"),
        ("cell_wall_SAR (plant)", "plant-specific defence with no animal counterpart", "CB2023"),
    ],
}


def provenance_coverage(module_key: str) -> Dict[str, object]:
    """Audit whether every transition name in the animal/plant nets is named in
    the transition-level provenance table for the module."""
    spec = MODULES[module_key]
    transition_names = sorted(
        {t.name for net in (spec["animal"](), spec["plant"]()) for t in net.transitions}
    )
    provenance_text = "\n".join(tr for tr, _, _ in MODEL_PROVENANCE[module_key])
    uncovered = [name for name in transition_names if name not in provenance_text]
    return {
        "module": module_key,
        "n_transitions": len(transition_names),
        "n_provenance_rows": len(MODEL_PROVENANCE[module_key]),
        "n_uncovered": len(uncovered),
        "uncovered": uncovered,
        "complete": len(uncovered) == 0,
    }


# ===========================================================================
# 7. CONSERVATION DATA (Phases 1-2) and HALLMARK COUNTS (Phase 1)
# ===========================================================================
# Gene counts per cancer-hallmark (Table 1 of Clavijo-Buritica et al. 2023):
# H. sapiens (associated genes) and A. thaliana (unique orthologs).
HALLMARK_GENE_COUNTS: Dict[str, Dict[str, int]] = {
    "AID": {"name": "Avoiding Immune Destruction", "human": 1063, "ath": 166, "prio": 0},
    "AIM": {"name": "Activating Invasion & Metastasis", "human": 1834, "ath": 252, "prio": 0},
    "DCE": {"name": "Deregulating Cellular Energetics", "human": 1086, "ath": 386, "prio": 1},
    "ERI": {"name": "Enabling Replicative Immortality", "human": 161, "ath": 59, "prio": 1},
    "EGS": {"name": "Evading Growth Suppressors", "human": 246, "ath": 34, "prio": 0},
    "GIM": {"name": "Genome Instability & Mutation", "human": 466, "ath": 167, "prio": 1},
    "IA": {"name": "Inducing Angiogenesis", "human": 337, "ath": 25, "prio": 0},
    "RCD": {"name": "Resisting Cell Death", "human": 1072, "ath": 211, "prio": 1},
    "SPS": {"name": "Sustaining Proliferative Signaling", "human": 1927, "ath": 454, "prio": 1},
    "TPI": {"name": "Tumor Promoting Inflammation", "human": 536, "ath": 39, "prio": 0},
}

# Curated conserved subnetworks per module: components with their plant ortholog
# and whether the function is conserved (evidence: Clavijo-Buritica et al. 2023;
# Quimbaya et al. 2012). (human_gene, arabidopsis_ortholog, role, conserved)
CONSERVED_SUBNETWORKS: Dict[str, List[Tuple[str, str, str, bool]]] = {
    "GIM": [
        ("ATM", "ATM (AT3G48190)", "DSB sensor", True),
        ("ATR", "ATR (AT5G40820)", "SSB sensor", True),
        ("CHK1", "WEE1 (AT1G02970)", "Transducer/arrest", True),
        ("CHK2", "WEE1 (AT1G02970)", "Transducer/arrest", True),
        ("CDKN1A/p21", "SMR (SMR1-13)", "CDK inhibitor", True),
        ("MCM2-7", "MCM2-7 (AtMCM)", "Replicative helicase", True),
        ("ORC1-6", "ORC1-6 (AtORC)", "Origin complex", True),
        ("BRCA1", "BRCA1 (AT4G21070)", "HR repair", True),
        ("TP53/p53", "-", "Apoptotic hub (not conserved)", False),
        ("CDC25", "-", "G2-M phosphatase (absent in plant)", False),
    ],
    "DCE": [
        ("HK/GCK", "HXK1 (AT4G29130)", "Glucokinase/hexokinase", True),
        ("PKM", "PK (AtPK)", "Pyruvate kinase", True),
        ("PDH", "PDH (AtPDH)", "Pyruvate dehydrogenase", True),
        ("CS", "CSY (AtCSY)", "Citrate synthase (TCA)", True),
        ("LDHA", "LDH (AT4G17260)", "Lactate DH (Warburg effect)", True),
        ("ATP5x", "ATP synthase (AtATP)", "ATP synthase (OXPHOS)", True),
        ("SDH", "SDH (AtSDH)", "Succinate DH (TCA)", True),
    ],
    "SPS": [
        ("RB1", "RBR (AT3G12280)", "RB-E2F repressor", True),
        ("E2F1-3", "E2Fa/b (AtE2F)", "E2F factor (G1-S)", True),
        ("CDK1/2", "CDKA;1 (AT3G48750)", "Cyclin-dependent kinase", True),
        ("CCNE/CCND", "CYCD (AtCYCD)", "G1 cyclin", True),
        ("MCMBP", "ETG1 (AT2G40550)", "Replisome regulator", True),
        ("HEATR6", "AT4G38120", "Division regulator", True),
        ("C14ORF21", "AT1G72320", "Division regulator", True),
    ],
    "RCD": [
        ("MTOR", "TOR (AT1G50030)", "Nutrient sensor", True),
        ("RPTOR", "RAPTOR (AtRAPTOR)", "TOR complex", True),
        ("ATG7", "ATG7 (AT5G45900)", "Autophagic conjugation", True),
        ("ATG5", "ATG5 (AT5G17290)", "Autophagosome", True),
        ("ATG8/LC3", "ATG8 (AtATG8)", "Autophagic elongation", True),
        ("PRKAA/AMPK", "SnRK1 (AtKIN10)", "Energy sensor", True),
        ("CASP3/7", "Metacaspase (AtMC)", "PCD execution (partial)", False),
        ("APAF1", "-", "Apoptosome (not conserved)", False),
    ],
    "AID": [
        ("TLR5", "FLS2 (AT5G46330)", "Recognition (convergent)", True),
        ("NOD/NLR", "NB-LRR (AtNLR)", "Intracellular receptor", True),
        ("MAPK", "MPK3/6 (AtMPK)", "Innate signal", True),
        ("IL/TCR", "-", "Adaptive immunity (absent)", False),
        ("BCR/Ig", "-", "Mobile receptors (absent)", False),
    ],
}


def conservation_index(module_key: str) -> Dict[str, float]:
    """Conservation index of a module subnetwork: the fraction of components
    with a conserved functional ortholog."""
    rows = CONSERVED_SUBNETWORKS[module_key]
    total = len(rows)
    conserved = sum(1 for *_, c in rows if c)
    return {
        "module": module_key,
        "total_components": total,
        "conserved_components": conserved,
        "conservation_index": conserved / total if total else 0.0,
    }


# ===========================================================================
# 8. High-level API
# ===========================================================================
def run_full_analysis(k: int = 6) -> List[Comparison]:
    """Run Phases 4-6 for every module and return the comparisons."""
    return [compare_module(m, k=k) for m in MODULES]


# --- Cross-organism portability (generalisation beyond plant-animal) --------
# The same engine compares any two module models over their shared interface.
# Here a single conserved module (the cell cycle) is compared between a human
# reference and a panel of model organisms, plus a scrambled same-alphabet
# control, to show the formal comparison API is not tied to Arabidopsis and is
# not fooled by shared labels alone.
CROSS_ORGANISM: Dict[str, object] = {
    "module": "Cell cycle (SPS/ERI)",
    "reference": ("Human", cellcycle_animal),
    "others": [
        ("Mouse", cellcycle_mouse),
        ("Yeast", cellcycle_yeast),
        ("Arabidopsis", cellcycle_plant),
        ("Scrambled-control", cellcycle_scrambled_control),
    ],
}


def compare_pair(ref_builder, other_builder, k: int = 6) -> Dict[str, object]:
    """Organism-agnostic comparison of two module models over their shared
    observational interface. Returns the behavioural properties and a verdict.
    The same routine underlies both the plant-animal analysis and the
    cross-organism demonstration, which is the point: nothing in it mentions any
    particular species."""
    lr = ref_builder().reachability_lts()
    lo = other_builder().reachability_lts()
    strong = strong_bisimilar(lr, lo)
    weak = weak_bisimilar(lr, lo)
    other_le_ref = weak_simulates(lo, lr)  # reference simulates the other
    ref_le_other = weak_simulates(lr, lo)  # the other simulates the reference
    dist = behavioural_distance(lr, lo, k=k)
    if strong:
        verdict = "Comparable (strong: near-identical core)"
    elif weak:
        verdict = "Comparable (weak bisimulation)"
    elif other_le_ref or ref_le_other:
        verdict = "Partial (simulation)"
    else:
        verdict = "Not comparable"
    return {
        "strong_bisimilar": strong,
        "weak_bisimilar": weak,
        "other_simulated_by_ref": other_le_ref,
        "ref_simulated_by_other": ref_le_other,
        "distance": dist,
        "verdict": verdict,
    }


def generalization_analysis(k: int = 6) -> List[Dict[str, object]]:
    """Apply the method to a panel of model organisms (Mouse, Yeast,
    Arabidopsis) and a scrambled same-alphabet control against a human reference
    for one conserved module, demonstrating that the framework is
    organism-agnostic and not fooled by shared labels alone."""
    ref_name, ref_builder = CROSS_ORGANISM["reference"]  # type: ignore[misc]
    rows: List[Dict[str, object]] = []
    for name, builder in CROSS_ORGANISM["others"]:  # type: ignore[union-attr]
        r = compare_pair(ref_builder, builder, k=k)
        rows.append({"reference": ref_name, "organism": name, **r})
    return rows


if __name__ == "__main__":
    print("== Partial behavioural comparison per module ==\n")
    for c in run_full_analysis():
        safe_h = MODULES[c.module]["animal"]().is_safe()
        safe_a = MODULES[c.module]["plant"]().is_safe()
        print(f"[{c.module}] {c.hallmark}")
        print(f"    states (animal/plant): {c.n_states_animal}/{c.n_states_plant}"
              f"   safe(1-bounded): {safe_h and safe_a}")
        print(f"    strong bisimulation  : {c.strong_bisimilar}")
        print(f"    weak bisimulation    : {c.weak_bisimilar}")
        print(f"    plant <= animal      : {c.plant_simulated_by_animal}")
        print(f"    animal <= plant      : {c.animal_simulated_by_plant}")
        print(f"    behavioural distance : {c.distance:.3f}")
        print(f"    -> VERDICT           : {c.verdict}\n")

    print("== Robustness (silent tau-refinement) and null baseline ==\n")
    quick_null = {
        r["module"]: r
        for r in null_baseline_suite(MODULES, n=2000, frac=0.6, seed=7)
    }
    for m in MODULES:
        rob = robustness_under_tau_refinement(m, n=300, n_ins=4, seed=7)
        nb = quick_null[m]
        print(f"[{m}] verdict preserved under refinement: "
              f"{rob['frac_verdict_preserved']*100:.0f}%   "
              f"observed d={nb['observed_distance']:.3f}  "
              f"null d={nb['null_mean']:.3f}+/-{nb['null_sd']:.3f}  "
              f"p={nb['p_value']:.3f}  q={nb['q_value_bh']:.3f}")

    print("\n== Cross-organism generalisation (cell-cycle module vs Human) ==\n")
    for r in generalization_analysis():
        print(f"[{r['organism']:>11} vs Human]  strong={r['strong_bisimilar']!s:>5}  "
              f"weak={r['weak_bisimilar']!s:>5}  d={r['distance']:.3f}  "
              f"-> {r['verdict']}")
