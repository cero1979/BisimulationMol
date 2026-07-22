"""Independent weak-simulation oracle and exhaustive finite validation.

The production implementation in :mod:`concurrent_biomodels` computes the
greatest simulation relation by deleting invalid state pairs.  This module uses
the dual attacker/defender game: it grows the least set of positions from which
an attacker can force a mismatch.  Agreement is checked exhaustively over every
LTS with one or two states and edge labels in ``{a, tau}``.
"""

from __future__ import annotations

from itertools import chain
from typing import Dict, Iterable, List, Sequence, Set, Tuple

try:
    from . import concurrent_biomodels as cbm
except ImportError:  # pragma: no cover - direct script execution
    import concurrent_biomodels as cbm


def weak_simulates_game(reference: cbm.LTS, candidate: cbm.LTS) -> bool:
    """Return whether ``candidate`` weakly simulates ``reference``.

    A game position is a state pair.  The attacker selects one outgoing move of
    the reference and the defender chooses a matching weak move.  Positions
    from which the attacker can force failure are accumulated as a least fixed
    point, independently of the relation-deletion implementation under test.
    """
    positions = [
        (left, right)
        for left in range(len(reference.states))
        for right in range(len(candidate.states))
    ]
    losing: Set[Tuple[int, int]] = set()
    changed = True
    while changed:
        changed = False
        for left, right in positions:
            if (left, right) in losing:
                continue
            for label, successor in reference._out[left]:
                replies = (
                    candidate.tau_closure(right)
                    if label == cbm.TAU
                    else candidate.weak_step(right, label)
                )
                if not replies or all((successor, reply) in losing for reply in replies):
                    losing.add((left, right))
                    changed = True
                    break
    return (reference.init, candidate.init) not in losing


def enumerate_lts(
    n_states: int,
    labels: Sequence[str] = ("a", cbm.TAU),
) -> Iterable[cbm.LTS]:
    """Enumerate every edge subset for a fixed state count and alphabet."""
    if n_states < 1:
        raise ValueError("n_states must be positive")
    possible_edges = [
        (source, label, target)
        for source in range(n_states)
        for label in labels
        for target in range(n_states)
    ]
    for mask in range(1 << len(possible_edges)):
        edges = [
            edge for index, edge in enumerate(possible_edges) if mask & (1 << index)
        ]
        yield cbm.LTS(
            name=f"exhaustive-{n_states}-{mask}",
            states=[f"s{state}" for state in range(n_states)],
            init=0,
            edges=edges,
        )


def exhaustive_simulation_validation(max_states: int = 2) -> Dict[str, object]:
    """Compare both algorithms on every ordered LTS pair up to ``max_states``."""
    if max_states < 1 or max_states > 2:
        raise ValueError("The declared exhaustive audit supports max_states in {1, 2}")
    systems: List[cbm.LTS] = list(
        chain.from_iterable(enumerate_lts(size) for size in range(1, max_states + 1))
    )
    disagreements = []
    agreement_count = 0
    for reference in systems:
        for candidate in systems:
            production = cbm.weak_simulates(reference, candidate)
            oracle = weak_simulates_game(reference, candidate)
            if production == oracle:
                agreement_count += 1
            elif len(disagreements) < 5:
                disagreements.append(
                    {
                        "reference": reference.name,
                        "candidate": candidate.name,
                        "production": production,
                        "game_oracle": oracle,
                    }
                )
    total = len(systems) ** 2
    return {
        "max_states": max_states,
        "alphabet": "a;tau",
        "number_of_lts": len(systems),
        "ordered_lts_pairs": total,
        "agreements": agreement_count,
        "disagreements": total - agreement_count,
        "complete_agreement": agreement_count == total,
        "counterexamples": disagreements,
        "oracle": "dual attacker-defender least-fixed-point game",
    }


def main() -> None:
    result = exhaustive_simulation_validation()
    for key, value in result.items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()
