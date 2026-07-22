"""Direct PN-GDDA comparison for native place/transition Petri nets.

The implementation follows Szawulak and Formanowicz (2022): connected induced
directed bipartite graphlets on two through five vertices, orbit-degree
distributions, inverse-degree scaling, and mean orbit agreement.  The published
151 graphlet topologies are generated rather than stored as drawings.

Holmes 1.1.1 and 2.0.1.2 expose 592 orbit slots.  A reconstruction from graph
automorphisms gives 576 distinct orbits; the difference is confined to twelve
five-node graphlets.  ``holmes_compatible=True`` reproduces the 592-slot Holmes
catalog, including its repeated and omitted symmetry slots.  The 576-orbit
catalog is retained as a sensitivity analysis, not substituted for PN-GDDA.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from functools import lru_cache
from itertools import combinations, permutations, product
from math import prod, sqrt
from typing import Dict, FrozenSet, Iterable, List, Mapping, Tuple

try:  # Package import (tests and external users).
    from . import concurrent_biomodels as cbm
except ImportError:  # Script/notebook import with ``src`` on sys.path.
    import concurrent_biomodels as cbm


PN_GDDA_EQUIVALENCE_THRESHOLD = 0.9
HOLMES_REFERENCE_SCORE = 0.987202746587073
HOLMES_111_SHA256 = "1747a9798c074a4e8a560cded9396ec3d0be05af2d948953c7730d5e623f044c"
HOLMES_2012_SHA256 = "e8e23527874d17285307d10b3ee54f8e6bd2cc6626b137f6f49e78afb6d9d810"
HOLMES_111_URL = "https://www.cs.put.poznan.pl/mradom/Holmes/HolmesRelease_111.zip"
HOLMES_2012_URL = "https://www.cs.put.poznan.pl/mradom/Holmes/Holmes_2_0.zip"

Code = Tuple[int, ...]
Signature = Tuple[int, int, Code]


@dataclass(frozen=True)
class GraphletCatalogEntry:
    """One canonical pn-graphlet and its global orbit slots."""

    place_count: int
    transition_count: int
    code: Code
    orbit_slots: Tuple[FrozenSet[int], ...]
    offset: int

    @property
    def signature(self) -> Signature:
        return (self.place_count, self.transition_count, self.code)

    @property
    def size(self) -> int:
        return self.place_count + self.transition_count


# The source paper reports 592 orbits.  Holmes 1.1.1 (June 2022) and Holmes
# 2.0.1.2 (November 2025) implement that count by refining the mathematical
# automorphism partition for these twelve graphlets.  Values are canonical
# vertex representatives, repeated exactly as the Holmes orbit slots occur.
# This compact compatibility map was reconstructed independently from both
# released JARs; all other graphlets use their automorphism orbits directly.
_HOLMES_ROOT_OVERRIDES: Mapping[Signature, Tuple[int, ...]] = {
    (3, 2, (1, 1, 1, 2, 2, 1)): (0, 1, 1, 3, 3),
    (3, 2, (1, 2, 2, 1, 2, 2)): (0, 0, 2, 3, 3),
    (3, 2, (1, 1, 1, 1, 1, 1)): (0, 3, 3),
    (3, 2, (1, 1, 1, 1, 2, 2)): (0, 2, 3, 3),
    (3, 2, (1, 1, 2, 2, 2, 2)): (1, 1, 3, 3),
    (3, 2, (2, 2, 2, 2, 2, 2)): (0, 3, 3),
    (2, 3, (1, 2, 2, 2, 1, 2)): (0, 0, 2, 2, 4),
    (2, 3, (1, 1, 2, 1, 2, 1)): (0, 0, 2, 3, 3),
    (2, 3, (2, 2, 2, 2, 2, 2)): (0, 0, 2),
    (2, 3, (1, 2, 2, 1, 2, 2)): (0, 0, 2, 3),
    (2, 3, (1, 1, 2, 1, 1, 2)): (0, 0, 2, 4),
    (2, 3, (1, 1, 1, 1, 1, 1)): (0, 0, 2),
}


def _connected(place_count: int, transition_count: int, code: Code) -> bool:
    size = place_count + transition_count
    adjacency = [set() for _ in range(size)]
    for place in range(place_count):
        for transition in range(transition_count):
            if code[place * transition_count + transition] == 0:
                continue
            target = place_count + transition
            adjacency[place].add(target)
            adjacency[target].add(place)

    seen = {0}
    stack = [0]
    while stack:
        node = stack.pop()
        for neighbour in adjacency[node] - seen:
            seen.add(neighbour)
            stack.append(neighbour)
    return len(seen) == size


def _canonical_code(place_count: int, transition_count: int, code: Code) -> Code:
    """Canonicalize a bipartite adjacency code under type-preserving relabeling."""
    candidates = []
    for place_order in permutations(range(place_count)):
        for transition_order in permutations(range(transition_count)):
            candidates.append(
                tuple(
                    code[place_order[p] * transition_count + transition_order[t]]
                    for p in range(place_count)
                    for t in range(transition_count)
                )
            )
    return min(candidates)


def _canonical_code_and_mapping(
    place_count: int, transition_count: int, code: Code
) -> Tuple[Code, Tuple[int, ...]]:
    """Return canonical code and map from current to canonical vertex indices."""
    best: Tuple[Code, Tuple[int, ...], Tuple[int, ...]] | None = None
    for place_order in permutations(range(place_count)):
        for transition_order in permutations(range(transition_count)):
            candidate = tuple(
                code[place_order[p] * transition_count + transition_order[t]]
                for p in range(place_count)
                for t in range(transition_count)
            )
            key = (candidate, place_order, transition_order)
            if best is None or key < best:
                best = key
    assert best is not None
    candidate, place_order, transition_order = best
    mapping = [0] * (place_count + transition_count)
    for canonical, current in enumerate(place_order):
        mapping[current] = canonical
    for canonical, current in enumerate(transition_order):
        mapping[place_count + current] = place_count + canonical
    return candidate, tuple(mapping)


def _directed_edges(
    place_count: int, transition_count: int, code: Code
) -> set[Tuple[int, int]]:
    edges: set[Tuple[int, int]] = set()
    for place in range(place_count):
        for transition in range(transition_count):
            value = code[place * transition_count + transition]
            target = place_count + transition
            if value == 1:
                edges.add((place, target))
            elif value == 2:
                edges.add((target, place))
    return edges


def _automorphism_orbits(
    place_count: int, transition_count: int, code: Code
) -> Tuple[FrozenSet[int], ...]:
    """Compute type- and direction-preserving vertex automorphism orbits."""
    size = place_count + transition_count
    edges = _directed_edges(place_count, transition_count, code)
    parent = list(range(size))

    def find(node: int) -> int:
        while parent[node] != node:
            parent[node] = parent[parent[node]]
            node = parent[node]
        return node

    def union(left: int, right: int) -> None:
        left_root = find(left)
        right_root = find(right)
        if left_root != right_root:
            parent[right_root] = left_root

    for place_image in permutations(range(place_count)):
        for transition_local in permutations(range(transition_count)):
            mapping = dict(enumerate(place_image))
            mapping.update(
                {
                    place_count + source: place_count + target
                    for source, target in enumerate(transition_local)
                }
            )
            if {(mapping[a], mapping[b]) for a, b in edges} != edges:
                continue
            for source, target in mapping.items():
                union(source, target)

    groups: Dict[int, set[int]] = {}
    for node in range(size):
        groups.setdefault(find(node), set()).add(node)
    return tuple(
        sorted((frozenset(group) for group in groups.values()), key=lambda x: min(x))
    )


@lru_cache(maxsize=1)
def graphlet_signatures() -> Tuple[Signature, ...]:
    """Generate the 151 connected directed bipartite graphlet topologies."""
    signatures = set()
    for size in range(2, 6):
        for place_count in range(1, size):
            transition_count = size - place_count
            for code in product(range(3), repeat=place_count * transition_count):
                if not _connected(place_count, transition_count, code):
                    continue
                signatures.add(
                    (
                        place_count,
                        transition_count,
                        _canonical_code(place_count, transition_count, code),
                    )
                )
    return tuple(
        sorted(signatures, key=lambda x: (x[0] + x[1], x[0], x[1], x[2]))
    )


@lru_cache(maxsize=2)
def graphlet_catalog(
    holmes_compatible: bool = True,
) -> Tuple[GraphletCatalogEntry, ...]:
    """Build either the published/Holmes 592-slot or corrected 576-orbit catalog."""
    result = []
    offset = 0
    for place_count, transition_count, code in graphlet_signatures():
        automorphism_orbits = _automorphism_orbits(
            place_count, transition_count, code
        )
        if holmes_compatible and (place_count, transition_count, code) in _HOLMES_ROOT_OVERRIDES:
            roots = _HOLMES_ROOT_OVERRIDES[(place_count, transition_count, code)]
            orbit_slots = tuple(
                next(orbit for orbit in automorphism_orbits if root in orbit)
                for root in roots
            )
        else:
            orbit_slots = automorphism_orbits
        result.append(
            GraphletCatalogEntry(
                place_count,
                transition_count,
                code,
                orbit_slots,
                offset,
            )
        )
        offset += len(orbit_slots)
    return tuple(result)


def catalog_summary(holmes_compatible: bool = True) -> List[Dict[str, int]]:
    """Return graphlet and orbit counts by graphlet size."""
    catalog = graphlet_catalog(holmes_compatible)
    rows = []
    for size in range(2, 6):
        selected = [entry for entry in catalog if entry.size == size]
        rows.append(
            {
                "size": size,
                "graphlets": len(selected),
                "orbits": sum(len(entry.orbit_slots) for entry in selected),
            }
        )
    return rows


def _net_structure(
    net: cbm.PetriNet,
) -> Tuple[Tuple[str, ...], Tuple[str, ...], Dict[Tuple[int, int], int]]:
    places = tuple(net.places)
    transitions = tuple(transition.name for transition in net.transitions)
    place_index = {name: index for index, name in enumerate(places)}
    weights: Dict[Tuple[int, int], int] = {}
    transition_offset = len(places)
    for transition_index, transition in enumerate(net.transitions):
        node = transition_offset + transition_index
        for place, weight in transition.pre.items():
            weights[(place_index[place], node)] = int(weight)
        for place, weight in transition.post.items():
            weights[(node, place_index[place])] = int(weight)
    return places, transitions, weights


def orbit_degree_vectors(
    net: cbm.PetriNet, holmes_compatible: bool = True
) -> List[Tuple[int, ...]]:
    """Count every induced pn-graphlet touching every Petri-net node."""
    places, transitions, weights = _net_structure(net)
    place_total = len(places)
    node_total = place_total + len(transitions)
    catalog = graphlet_catalog(holmes_compatible)
    catalog_by_signature = {entry.signature: entry for entry in catalog}
    orbit_total = sum(len(entry.orbit_slots) for entry in catalog)
    vectors = [[0] * orbit_total for _ in range(node_total)]

    for size in range(2, min(5, node_total) + 1):
        for subset in combinations(range(node_total), size):
            subset_places = tuple(node for node in subset if node < place_total)
            subset_transitions = tuple(node for node in subset if node >= place_total)
            if not subset_places or not subset_transitions:
                continue
            place_count = len(subset_places)
            transition_count = len(subset_transitions)
            code_values = []
            invalid_parallel_pair = False
            occurrence_weights = []
            for place in subset_places:
                for transition in subset_transitions:
                    forward = weights.get((place, transition), 0)
                    backward = weights.get((transition, place), 0)
                    if forward and backward:
                        invalid_parallel_pair = True
                        break
                    if forward:
                        code_values.append(1)
                        occurrence_weights.append(forward)
                    elif backward:
                        code_values.append(2)
                        occurrence_weights.append(backward)
                    else:
                        code_values.append(0)
                if invalid_parallel_pair:
                    break
            if invalid_parallel_pair:
                continue
            code = tuple(code_values)
            if not _connected(place_count, transition_count, code):
                continue
            canonical, mapping = _canonical_code_and_mapping(
                place_count, transition_count, code
            )
            entry = catalog_by_signature[(place_count, transition_count, canonical)]
            multiplicity = prod(occurrence_weights)
            local_nodes = subset_places + subset_transitions
            for local_index, net_node in enumerate(local_nodes):
                canonical_node = mapping[local_index]
                for slot, orbit in enumerate(entry.orbit_slots):
                    if canonical_node in orbit:
                        vectors[net_node][entry.offset + slot] += multiplicity
    return [tuple(row) for row in vectors]


def _normalised_distribution(values: Iterable[int]) -> Dict[int, float]:
    frequencies = Counter(value for value in values if value > 0)
    scaled = {degree: count / degree for degree, count in frequencies.items()}
    denominator = sum(scaled.values())
    if denominator == 0:
        return {}
    return {degree: value / denominator for degree, value in scaled.items()}


def pn_gdda_similarity(
    left: cbm.PetriNet,
    right: cbm.PetriNet,
    holmes_compatible: bool = True,
) -> float:
    """Compute the mean PN graphlet-degree-distribution agreement in [0, 1]."""
    left_vectors = orbit_degree_vectors(left, holmes_compatible)
    right_vectors = orbit_degree_vectors(right, holmes_compatible)
    orbit_total = len(left_vectors[0]) if left_vectors else len(right_vectors[0])
    agreements = []
    for orbit in range(orbit_total):
        left_distribution = _normalised_distribution(row[orbit] for row in left_vectors)
        right_distribution = _normalised_distribution(row[orbit] for row in right_vectors)
        degrees = set(left_distribution) | set(right_distribution)
        distance = sqrt(
            sum(
                (
                    left_distribution.get(degree, 0.0)
                    - right_distribution.get(degree, 0.0)
                )
                ** 2
                for degree in degrees
            )
        )
        agreements.append(1.0 - distance / sqrt(2.0))
    return sum(agreements) / len(agreements)


def state_machine_petri(lts: cbm.LTS, name: str | None = None) -> cbm.PetriNet:
    """Encode an LTS exactly as a one-token state-machine Petri net."""
    places = [f"state_{index}" for index in range(len(lts.states))]
    transitions = [
        cbm.Transition(
            name=f"edge_{index}_{source}_{target}",
            pre={places[source]: 1},
            post={places[target]: 1},
            label=label,
        )
        for index, (source, label, target) in enumerate(lts.edges)
    ]
    return cbm.PetriNet(
        name or f"{lts.name}-state-machine",
        transitions,
        {places[lts.init]: 1},
    )


def holmes_reference_pair() -> Tuple[cbm.PetriNet, cbm.PetriNet]:
    """Return the four-node pair independently evaluated with Holmes 1.1.1.

    The left net is the complete directed K2,2 input net. The right net lacks
    only the arc from ``p1`` to ``t1``. It exercises ten non-identical orbit
    distributions while remaining small enough that Holmes' greedy occurrence
    finder and exact induced enumeration visit the same occurrences.
    """
    left = cbm.PetriNet(
        "Holmes-reference-K22",
        [
            cbm.Transition("t0", {"p0": 1, "p1": 1}, {}, "a"),
            cbm.Transition("t1", {"p0": 1, "p1": 1}, {}, "b"),
        ],
        {"p0": 1, "p1": 1},
    )
    right = cbm.PetriNet(
        "Holmes-reference-K22-minus-arc",
        [
            cbm.Transition("t0", {"p0": 1, "p1": 1}, {}, "a"),
            cbm.Transition("t1", {"p0": 1}, {}, "b"),
        ],
        {"p0": 1, "p1": 1},
    )
    return left, right


def catalog_validation() -> Dict[str, object]:
    """Machine-readable catalog audit and independent Holmes score check."""
    left, right = holmes_reference_pair()
    observed = pn_gdda_similarity(left, right, holmes_compatible=True)
    return {
        "definition": "connected induced directed bipartite graphlets of 2-5 nodes",
        "published_holmes_catalog": catalog_summary(True),
        "automorphism_partition_sensitivity": catalog_summary(False),
        "published_graphlet_total": len(graphlet_catalog(True)),
        "published_orbit_slot_total": sum(
            len(entry.orbit_slots) for entry in graphlet_catalog(True)
        ),
        "automorphism_orbit_total": sum(
            len(entry.orbit_slots) for entry in graphlet_catalog(False)
        ),
        "holmes_reference_version": "Holmes 1.1.1 (June 2022)",
        "holmes_reference_download": HOLMES_111_URL,
        "holmes_reference_jar_sha256": HOLMES_111_SHA256,
        "holmes_latest_catalog_checked": "Holmes 2.0.1.2 (November 2025)",
        "holmes_latest_download": HOLMES_2012_URL,
        "holmes_latest_jar_sha256": HOLMES_2012_SHA256,
        "holmes_reference_score": HOLMES_REFERENCE_SCORE,
        "independent_python_score": observed,
        "absolute_score_difference": abs(observed - HOLMES_REFERENCE_SCORE),
        "score_agreement_at_12_decimals": round(observed, 12)
        == round(HOLMES_REFERENCE_SCORE, 12),
        "main_analysis_catalog": "published/Holmes 151 graphlets and 592 orbit slots",
        "sensitivity_catalog": "151 graphlets and 576 automorphism-distinct orbits",
    }


def native_module_comparisons(k: int = 6) -> List[Dict[str, object]]:
    """Compare every curated animal/plant Petri-net pair directly with PN-GDDA."""
    rows: List[Dict[str, object]] = []
    for module, specification in cbm.MODULES.items():
        animal = specification["animal"]()
        plant = specification["plant"]()
        formal = cbm.compare_module(module, k=k)
        published = pn_gdda_similarity(animal, plant, holmes_compatible=True)
        corrected = pn_gdda_similarity(animal, plant, holmes_compatible=False)
        if formal.weak_bisimilar:
            formal_class = "weak equivalence"
        elif formal.plant_simulated_by_animal or formal.animal_simulated_by_plant:
            formal_class = "one-way simulation"
        else:
            formal_class = "not comparable"
        rows.append(
            {
                "module": module,
                "animal_net": animal.name,
                "plant_net": plant.name,
                "animal_places": len(animal.places),
                "animal_transitions": len(animal.transitions),
                "plant_places": len(plant.places),
                "plant_transitions": len(plant.transitions),
                "pn_gdda_592_similarity": published,
                "pn_gdda_576_similarity": corrected,
                "catalog_sensitivity_delta": corrected - published,
                "pn_gdda_equivalent_at_0_9": published
                >= PN_GDDA_EQUIVALENCE_THRESHOLD,
                "weak_bisimilar": formal.weak_bisimilar,
                "plant_simulated_by_animal": formal.plant_simulated_by_animal,
                "animal_simulated_by_plant": formal.animal_simulated_by_plant,
                "formal_class": formal_class,
                "formal_verdict": formal.verdict,
            }
        )
    return rows


if __name__ == "__main__":
    print("Published/Holmes catalog:", catalog_summary(True))
    print("Automorphism-corrected catalog:", catalog_summary(False))
    validation = catalog_validation()
    print(
        "Holmes 1.1.1 reference:",
        f"Holmes={validation['holmes_reference_score']:.15f}",
        f"Python={validation['independent_python_score']:.15f}",
        f"12-decimal agreement={validation['score_agreement_at_12_decimals']}",
    )
    for module, specification in cbm.MODULES.items():
        left = specification["animal"]()
        right = specification["plant"]()
        print(
            module,
            f"PN-GDDA-592={pn_gdda_similarity(left, right, True):.6f}",
            f"PN-GDDA-576={pn_gdda_similarity(left, right, False):.6f}",
        )
