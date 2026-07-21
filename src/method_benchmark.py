"""Independent benchmark for the qualitative model-comparison framework.

The biological case study contains hand-curated models, so it cannot by itself
establish that the comparison algorithm distinguishes known behavioural
relations.  This module supplies deterministic synthetic pairs with construction-
level ground truth, two deliberately simple non-formal baselines, and a runtime
scaling experiment.  It depends only on the Python standard library and the
formal engine in :mod:`concurrent_biomodels`.
"""

from __future__ import annotations

import random
import statistics
import time
from collections import Counter
from dataclasses import dataclass
from typing import Callable, Dict, Iterable, List, Sequence, Tuple

try:  # Package import (tests and external users).
    from . import concurrent_biomodels as cbm
except ImportError:  # Script/notebook import with ``src`` on sys.path.
    import concurrent_biomodels as cbm


@dataclass(frozen=True)
class BenchmarkCase:
    """One model pair with a relation fixed by its construction."""

    case: str
    reference: cbm.LTS
    candidate: cbm.LTS
    expected_class: str
    rationale: str


def linear_workflow(n_steps: int, labels: Sequence[str] = ("a", "b", "c", "d")) -> cbm.LTS:
    """Create a deterministic labelled workflow with ``n_steps`` transitions."""
    if n_steps < 2:
        raise ValueError("n_steps must be at least 2")
    if not labels:
        raise ValueError("labels must not be empty")
    states = [f"s{i}" for i in range(n_steps + 1)]
    edges = [(i, labels[i % len(labels)], i + 1) for i in range(n_steps)]
    return cbm.LTS(f"workflow-{n_steps}", states, 0, edges)


def clone_lts(lts: cbm.LTS, name: str) -> cbm.LTS:
    return cbm.LTS(name, list(lts.states), lts.init, list(lts.edges))


def swap_adjacent_labels(lts: cbm.LTS, first_edge: int) -> cbm.LTS:
    """Swap labels on adjacent chain edges while preserving topology and counts."""
    edges = list(lts.edges)
    if first_edge < 0 or first_edge + 1 >= len(edges):
        raise ValueError("first_edge must identify two adjacent edges")
    s1, a1, d1 = edges[first_edge]
    s2, a2, d2 = edges[first_edge + 1]
    edges[first_edge] = (s1, a2, d1)
    edges[first_edge + 1] = (s2, a1, d2)
    return cbm.LTS(lts.name + "-reordered", list(lts.states), lts.init, edges)


def add_observable_branch(lts: cbm.LTS, source: int, label: str = "x") -> cbm.LTS:
    """Add behaviour without removing the reference workflow."""
    states = list(lts.states) + [f"branch{len(lts.states)}"]
    edges = list(lts.edges) + [(source, label, len(states) - 1)]
    return cbm.LTS(lts.name + "-branch", states, lts.init, edges)


def branching_time_trap() -> Tuple[cbm.LTS, cbm.LTS]:
    """Return trace-equivalent systems that differ in when choice is resolved.

    The reference performs ``a`` and then offers ``b`` or ``c``.  The candidate
    chooses one of two ``a`` transitions first and can then offer only ``b`` or
    only ``c``.  Their observable trace sets are identical, but the candidate is
    only simulated by the reference; they are not bisimilar.
    """
    reference = cbm.LTS(
        "late-choice",
        ["r0", "r1", "rb", "rc"],
        0,
        [(0, "a", 1), (1, "b", 2), (1, "c", 3)],
    )
    candidate = cbm.LTS(
        "early-choice",
        ["q0", "qb", "qc", "qbt", "qct"],
        0,
        [(0, "a", 1), (0, "a", 2), (1, "b", 3), (2, "c", 4)],
    )
    return reference, candidate


def synthetic_cases(n_steps: int = 12, seed: int = 17) -> List[BenchmarkCase]:
    """Build the predeclared synthetic validation suite."""
    base = linear_workflow(n_steps)
    identical = clone_lts(base, "identical")
    refined = cbm.refine_with_tau(base, random.Random(seed), max(1, n_steps // 4))

    middle_label = base.edges[n_steps // 2][1]
    mismatch = cbm.relabel_observable(base, middle_label, middle_label + "_mismatch")
    reordered = swap_adjacent_labels(base, max(1, n_steps // 2 - 1))
    extension = add_observable_branch(base, max(1, n_steps // 2), "extra_outcome")
    late, early = branching_time_trap()

    return [
        BenchmarkCase(
            "identity",
            base,
            identical,
            "strong equivalence",
            "Exact copy; every labelled transition is preserved.",
        ),
        BenchmarkCase(
            "silent refinement",
            base,
            refined,
            "weak equivalence",
            "Observable transitions are subdivided by internal tau steps.",
        ),
        BenchmarkCase(
            "label mismatch",
            base,
            mismatch,
            "not comparable",
            "One recurring observable is replaced by an unmatched label.",
        ),
        BenchmarkCase(
            "label order swap",
            base,
            reordered,
            "not comparable",
            "Topology and label counts are fixed but observable order changes.",
        ),
        BenchmarkCase(
            "added branch",
            base,
            extension,
            "reference simulated by candidate",
            "The candidate preserves the workflow and adds an extra outcome.",
        ),
        BenchmarkCase(
            "trace-equivalent branching",
            late,
            early,
            "candidate simulated by reference",
            "Trace sets agree, but choice is resolved at a different time.",
        ),
    ]


def _ratio_similarity(a: int, b: int) -> float:
    if a == b == 0:
        return 1.0
    return min(a, b) / max(a, b)


def _weighted_jaccard(a: Counter, b: Counter) -> float:
    keys = set(a) | set(b)
    denominator = sum(max(a[k], b[k]) for k in keys)
    if denominator == 0:
        return 1.0
    return sum(min(a[k], b[k]) for k in keys) / denominator


def structural_profile_similarity(l1: cbm.LTS, l2: cbm.LTS) -> float:
    """Feature-only baseline in [0, 1], intentionally blind to event order.

    The score averages state-count, edge-count, observable-label multiset and
    out-degree multiset similarities.  It is a transparent baseline for showing
    why matched graph summaries are insufficient for behavioural comparison; it
    is not presented as a replacement for a network-alignment algorithm.
    """
    labels1 = Counter(a for _, a, _ in l1.edges)
    labels2 = Counter(a for _, a, _ in l2.edges)
    out1 = Counter(len(l1._out[s]) for s in range(len(l1.states)))
    out2 = Counter(len(l2._out[s]) for s in range(len(l2.states)))
    components = (
        _ratio_similarity(len(l1.states), len(l2.states)),
        _ratio_similarity(len(l1.edges), len(l2.edges)),
        _weighted_jaccard(labels1, labels2),
        _weighted_jaccard(out1, out2),
    )
    return sum(components) / len(components)


def classify_pair(reference: cbm.LTS, candidate: cbm.LTS, k: int = 8) -> Dict[str, object]:
    """Apply all formal relations and both non-formal baselines to one pair."""
    strong = cbm.strong_bisimilar(reference, candidate)
    weak = cbm.weak_bisimilar(reference, candidate)
    ref_le_candidate = cbm.weak_simulates(reference, candidate)
    candidate_le_ref = cbm.weak_simulates(candidate, reference)
    distance = cbm.behavioural_distance(reference, candidate, k=k)

    if strong:
        formal_class = "strong equivalence"
    elif weak:
        formal_class = "weak equivalence"
    elif ref_le_candidate and candidate_le_ref:
        formal_class = "mutual simulation"
    elif ref_le_candidate:
        formal_class = "reference simulated by candidate"
    elif candidate_le_ref:
        formal_class = "candidate simulated by reference"
    else:
        formal_class = "not comparable"

    structural = structural_profile_similarity(reference, candidate)
    return {
        "strong_bisimilar": strong,
        "weak_bisimilar": weak,
        "reference_simulated_by_candidate": ref_le_candidate,
        "candidate_simulated_by_reference": candidate_le_ref,
        "trace_distance": distance,
        "trace_equivalent_at_k": abs(distance) < 1e-12,
        "structural_similarity": structural,
        "structurally_equivalent_at_0_9": structural >= 0.9,
        "formal_class": formal_class,
        "n_states_reference": len(reference.states),
        "n_states_candidate": len(candidate.states),
        "n_edges_reference": len(reference.edges),
        "n_edges_candidate": len(candidate.edges),
    }


def validation_benchmark(n_steps: int = 12, seed: int = 17, k: int = 8) -> List[Dict[str, object]]:
    """Run all synthetic cases and compare computed with expected relations."""
    rows: List[Dict[str, object]] = []
    for case in synthetic_cases(n_steps=n_steps, seed=seed):
        result = classify_pair(case.reference, case.candidate, k=k)
        result.update(
            {
                "case": case.case,
                "expected_class": case.expected_class,
                "formal_match": result["formal_class"] == case.expected_class,
                "expected_weak_equivalent": case.expected_class
                in {"strong equivalence", "weak equivalence"},
                "rationale": case.rationale,
            }
        )
        rows.append(result)
    return rows


def baseline_accuracy(rows: Iterable[Dict[str, object]]) -> List[Dict[str, object]]:
    """Binary equivalence accuracy for the formal, trace and profile methods."""
    records = list(rows)
    expected = [bool(r["expected_weak_equivalent"]) for r in records]
    predictions = {
        "weak bisimulation": [bool(r["weak_bisimilar"]) for r in records],
        "trace equality (k=8)": [bool(r["trace_equivalent_at_k"]) for r in records],
        "structural profile (>=0.9)": [
            bool(r["structurally_equivalent_at_0_9"]) for r in records
        ],
    }
    summary = []
    for method, predicted in predictions.items():
        tp = sum(p and e for p, e in zip(predicted, expected))
        tn = sum((not p) and (not e) for p, e in zip(predicted, expected))
        fp = sum(p and (not e) for p, e in zip(predicted, expected))
        fn = sum((not p) and e for p, e in zip(predicted, expected))
        summary.append(
            {
                "method": method,
                "accuracy": (tp + tn) / len(expected),
                "true_positive": tp,
                "true_negative": tn,
                "false_positive": fp,
                "false_negative": fn,
                "n_cases": len(expected),
            }
        )
    return summary


def _median_runtime_ms(operation: Callable[[], object], repeats: int) -> float:
    samples = []
    for _ in range(repeats):
        start = time.perf_counter()
        operation()
        samples.append((time.perf_counter() - start) * 1000.0)
    return statistics.median(samples)


def scalability_benchmark(
    sizes: Sequence[int] = (8, 16, 32, 64, 96, 128),
    repeats: int = 3,
    seed: int = 23,
) -> List[Dict[str, object]]:
    """Measure runtime growth on identity and silent-refinement pairs.

    Timings are machine-dependent and therefore excluded from bit-for-bit
    reproducibility checks.  State/edge counts, relation outcomes and candidate
    relation sizes are deterministic and are checked by the test suite.
    """
    if repeats < 1:
        raise ValueError("repeats must be positive")
    rows: List[Dict[str, object]] = []
    for n_steps in sizes:
        base = linear_workflow(n_steps)
        variants = {
            "identity": clone_lts(base, f"workflow-{n_steps}-copy"),
            "silent refinement": cbm.refine_with_tau(
                base, random.Random(seed + n_steps), max(1, n_steps // 8)
            ),
        }
        for variant, candidate in variants.items():
            operations = {
                "strong_bisimulation_ms": lambda b=base, c=candidate: cbm.strong_bisimilar(b, c),
                "weak_bisimulation_ms": lambda b=base, c=candidate: cbm.weak_bisimilar(b, c),
                "two_simulations_ms": lambda b=base, c=candidate: (
                    cbm.weak_simulates(b, c), cbm.weak_simulates(c, b)
                ),
                "trace_distance_ms": lambda b=base, c=candidate: cbm.behavioural_distance(b, c, k=8),
            }
            timings = {
                name: _median_runtime_ms(operation, repeats)
                for name, operation in operations.items()
            }
            classified = classify_pair(base, candidate, k=8)
            rows.append(
                {
                    "n_steps": n_steps,
                    "variant": variant,
                    "n_states_reference": len(base.states),
                    "n_states_candidate": len(candidate.states),
                    "n_edges_reference": len(base.edges),
                    "n_edges_candidate": len(candidate.edges),
                    "candidate_relation_pairs": len(base.states) * len(candidate.states),
                    **timings,
                    "total_runtime_ms": sum(timings.values()),
                    "formal_class": classified["formal_class"],
                    "repeats": repeats,
                }
            )
    return rows


if __name__ == "__main__":
    validation = validation_benchmark()
    print("Synthetic benchmark")
    for row in validation:
        print(
            f"{row['case']:<27} expected={row['expected_class']:<32} "
            f"observed={row['formal_class']}"
        )
    print("\nBaseline accuracy")
    for row in baseline_accuracy(validation):
        print(
            f"{row['method']:<30} accuracy={row['accuracy']:.3f} "
            f"FP={row['false_positive']} FN={row['false_negative']}"
        )
