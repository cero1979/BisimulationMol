"""Blind, data-backed validation on public HPN-DREAM Boolean networks.

Three independently inferred model families (BT20, BT549 and MCF7) are reduced
to one structure-only medoid per cell line.  The medoid selection never reads
the held-out mTOR-inhibitor data.  The selected models are then compared under
the intersection of public test perturbations and readouts.  Their asynchronous
LTS relations are cross-checked with mCRL2 and related to experimental profile
distances with an exact condition-stratified permutation test.
The pairwise classifications are also repeated under global synchronous updates
to expose semantic sensitivity without replacing the CASPOTS-compatible primary
asynchronous analysis.

This module intentionally uses only the Python standard library plus the local
formal engine.  The optional CASPOTS reproduction is in
``scripts/run_caspots_hpn_validation.py`` because it requires Clingo, CASPO and
NuSMV.
"""

from __future__ import annotations

import csv
import hashlib
import itertools
import json
import math
import statistics
from collections import defaultdict, deque
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from typing import Dict, Iterable, List, Mapping, Sequence, Tuple

try:
    from . import concurrent_biomodels as cbm
    from . import method_benchmark as mb
    from . import public_validation as pv
except ImportError:  # pragma: no cover - direct script execution
    import concurrent_biomodels as cbm
    import method_benchmark as mb
    import public_validation as pv


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "hpn_dream"
RESULTS = ROOT / "results"

CELLS = ("BT20", "BT549", "MCF7")
FAMILY_FILES = {cell: DATA / f"{cell}_family.csv" for cell in CELLS}
TEST_FILES = {cell: DATA / f"{cell}_test.csv" for cell in CELLS}

EXPECTED_HASHES = {
    "merged_pkn.sif": "9eb1266e6f70764986afffc6a2728adcd6fd17d5cd625526d8601cab5c7adec3",
    "BT20_family.csv": "c1fb52005641d705b81aec28983bb53c2dab1969c4c53a2bd24397fe5f45cd6e",
    "BT549_family.csv": "d0912091719881cc3c1a271d7454ddd2f1f19b39f9f7a8fa75b707e4c13c2a7c",
    "MCF7_family.csv": "9f41c4020dd0f4d589dfc35af4052f23a7abde8f8ea4dc3346ab1cbcc9626feb",
    "BT20_learning.csv": "d8e7195b2db52c24829bb8662d6015140f7147b7606fc76dfe613f2e42d3305e",
    "BT549_learning.csv": "a5ca48bf621cf0d9f912e25ff75fd9e96d40336882f895ae10009f0750eb0725",
    "MCF7_learning.csv": "46dee96500d9ceca38f30c132be2f0fb03dbebac49309f26d85634ee9fd45c2d",
    "BT20_test.csv": "19861374078c538e6add650dce0c47f85282747a46316da9feeb25828a4ee857",
    "BT549_test.csv": "bf2fd40cad5f8aa9b42efc56dca245eee48afe7117e705a4daa5bca4d35c9559",
    "MCF7_test.csv": "b81175a4d97689ee6f8e1d002e92ad7cf04b4067838e8d56ca467826c2458a5c",
}

# Declared before inspecting response values: common PI3K/MAPK/mTOR readouts and
# the exact intersection of held-out perturbations in the three cell lines.
INTERFACE = (
    "4EBP1_pS65",
    "AKT_pT308",
    "BAD_pS112",
    "MAPK_pT202_Y204",
    "MEK1_pS217_S221",
    "mTOR_pS2448",
    "p70S6K_pT389",
)


@dataclass(frozen=True)
class Condition:
    name: str
    stimuli: Tuple[str, ...]
    inhibitors: Tuple[str, ...]


COMMON_CONDITIONS = (
    Condition("mTORi", (), ("mTOR_pS2448",)),
    Condition("IGF1+mTORi", ("IGF1",), ("mTOR_pS2448",)),
    Condition("4EBP1+mTORi", ("4EBP1_pS65",), ("mTOR_pS2448",)),
)


@dataclass(frozen=True)
class Literal:
    node: str
    positive: bool


@dataclass(frozen=True)
class Clause:
    target: str
    literals: Tuple[Literal, ...]
    source: str


@dataclass(frozen=True)
class Medoid:
    cell_line: str
    row_index: int
    clauses: Tuple[str, ...]
    family_size: int
    mean_jaccard: float


@dataclass(frozen=True)
class Experiment:
    cell_line: str
    stimuli: Tuple[str, ...]
    inhibitors: Tuple[str, ...]
    observations: Mapping[int, Mapping[str, float]]


@dataclass(frozen=True)
class BooleanModel:
    name: str
    rules: Mapping[str, Tuple[Clause, ...]]

    @property
    def variables(self) -> Tuple[str, ...]:
        nodes = set(self.rules)
        for clauses in self.rules.values():
            for clause in clauses:
                nodes.update(literal.node for literal in clause.literals)
        return tuple(sorted(nodes))


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_artifacts() -> None:
    missing = [name for name in EXPECTED_HASHES if not (DATA / name).is_file()]
    if missing:
        raise FileNotFoundError(
            "Missing HPN-DREAM artifacts: " + ", ".join(missing)
            + ". Run 'make hpn-data'."
        )
    for name, expected in EXPECTED_HASHES.items():
        observed = _sha256(DATA / name)
        if observed != expected:
            raise ValueError(
                f"SHA-256 mismatch for {name}: expected {expected}, observed {observed}"
            )


def load_family(cell_line: str) -> Tuple[Tuple[str, ...], List[Tuple[str, ...]]]:
    path = FAMILY_FILES[cell_line]
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.reader(handle)
        header = tuple(next(reader))
        models = []
        for row in reader:
            if not row:
                continue
            if len(row) != len(header):
                raise ValueError(f"Malformed model row in {path}: {len(row)} != {len(header)}")
            active = tuple(sorted(name for name, value in zip(header, row) if int(value)))
            models.append(active)
    if not models:
        raise ValueError(f"Empty model family: {path}")
    return header, models


def _jaccard(left: Iterable[str], right: Iterable[str]) -> float:
    a, b = set(left), set(right)
    union = a | b
    return len(a & b) / len(union) if union else 1.0


def select_medoid(cell_line: str) -> Medoid:
    """Select a family medoid from clauses only; no test file is opened."""
    _, models = load_family(cell_line)
    scores = []
    for index, model in enumerate(models):
        left = set(model)
        total = sum(
            (
                Fraction(len(left & set(other)), len(left | set(other)))
                if left | set(other)
                else Fraction(1)
            )
            for other in models
        )
        scores.append((total, model, index))
    maximum = max(score for score, _, _ in scores)
    clauses, index = min(
        (model, index) for score, model, index in scores if score == maximum
    )
    return Medoid(
        cell_line, index, clauses, len(models), float(maximum / len(models))
    )


def medoid_summary() -> List[Dict[str, object]]:
    rows = []
    medoids = {cell: select_medoid(cell) for cell in CELLS}
    for cell in CELLS:
        medoid = medoids[cell]
        rows.append(
            {
                "cell_line": cell,
                "family_size": medoid.family_size,
                "medoid_row_zero_based": medoid.row_index,
                "active_clauses": len(medoid.clauses),
                "mean_within_family_jaccard": medoid.mean_jaccard,
                "selection_uses_heldout_data": False,
                "family_sha256": EXPECTED_HASHES[f"{cell}_family.csv"],
                "test_sha256": EXPECTED_HASHES[f"{cell}_test.csv"],
            }
        )
    return rows


def parse_clause(source: str) -> Clause:
    try:
        target, expression = source.split("<-", 1)
    except ValueError as error:
        raise ValueError(f"Unsupported Boolean clause: {source}") from error
    literals = []
    for token in expression.split("+"):
        token = token.strip()
        positive = not token.startswith("!")
        literals.append(Literal(token[1:] if not positive else token, positive))
    return Clause(target.strip(), tuple(literals), source)


def model_from_medoid(medoid: Medoid) -> BooleanModel:
    rules: Dict[str, List[Clause]] = defaultdict(list)
    for source in medoid.clauses:
        clause = parse_clause(source)
        rules[clause.target].append(clause)
    return BooleanModel(
        name=f"{medoid.cell_line}_medoid",
        rules={target: tuple(sorted(clauses, key=lambda item: item.source))
               for target, clauses in sorted(rules.items())},
    )


def _intervention_name(column: str) -> Tuple[str, bool]:
    name = column[3:]
    if name.endswith(("i", "I")):
        return name[:-1], True
    return name, False


def load_experiments(cell_line: str) -> List[Experiment]:
    path = TEST_FILES[cell_line]
    with path.open(newline="", encoding="utf-8-sig") as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        raise ValueError(f"Empty test data: {path}")

    tr_columns = [name for name in rows[0] if name.startswith("TR:")]
    da_columns = [name for name in rows[0] if name.startswith("DA:")]
    dv_columns = [name for name in rows[0] if name.startswith("DV:")]
    observations_by_condition: Dict[
        Tuple[Tuple[str, ...], Tuple[str, ...]], Dict[int, Dict[str, float]]
    ] = defaultdict(dict)

    for row in rows:
        stimuli, inhibitors = [], []
        for column in tr_columns:
            if column.endswith(":CellLine") or float(row[column] or 0) != 1.0:
                continue
            name, inhibitor = _intervention_name(column)
            (inhibitors if inhibitor else stimuli).append(name)
        times = {int(float(row[name])) for name in da_columns if row[name] != ""}
        if len(times) != 1:
            raise ValueError(f"Expected one shared time per row in {path}, got {times}")
        time = times.pop()
        observed = {
            name[3:]: float(row[name])
            for name in dv_columns
            if row[name] not in ("", "NA", "NaN")
        }
        key = (tuple(sorted(stimuli)), tuple(sorted(inhibitors)))
        if time in observations_by_condition[key]:
            raise ValueError(f"Duplicate time {time} for {cell_line} condition {key}")
        observations_by_condition[key][time] = observed

    return [
        Experiment(cell_line, stimuli, inhibitors, dict(sorted(observations.items())))
        for (stimuli, inhibitors), observations in sorted(observations_by_condition.items())
    ]


def get_experiment(cell_line: str, condition: Condition) -> Experiment:
    wanted = (tuple(sorted(condition.stimuli)), tuple(sorted(condition.inhibitors)))
    matches = [
        experiment
        for experiment in load_experiments(cell_line)
        if (experiment.stimuli, experiment.inhibitors) == wanted
    ]
    if len(matches) != 1:
        raise ValueError(f"Expected one {condition.name} experiment for {cell_line}, got {len(matches)}")
    return matches[0]


def _relevant_nodes(model: BooleanModel, interface: Sequence[str]) -> Tuple[str, ...]:
    relevant = set(interface)
    queue = deque(interface)
    while queue:
        target = queue.popleft()
        for clause in model.rules.get(target, ()):
            for literal in clause.literals:
                if literal.node not in relevant:
                    relevant.add(literal.node)
                    queue.append(literal.node)
    return tuple(sorted(relevant))


def _evaluate(clauses: Sequence[Clause], state: Mapping[str, bool]) -> bool:
    return any(
        all(state.get(literal.node, False) == literal.positive for literal in clause.literals)
        for clause in clauses
    )


def _conditioned_initial_state(
    model: BooleanModel,
    experiment: Experiment,
    interface: Sequence[str],
    hidden_initial: bool,
) -> Tuple[
    Tuple[str, ...],
    Dict[str, int],
    Tuple[bool, ...],
    Dict[str, bool],
    Tuple[str, ...],
]:
    nodes = _relevant_nodes(model, interface)
    index = {node: position for position, node in enumerate(nodes)}
    initial = [hidden_initial] * len(nodes)
    time_zero = experiment.observations.get(0, {})
    for node, value in time_zero.items():
        if node in index:
            initial[index[node]] = value >= 0.5
    clamped: Dict[str, bool] = {name: True for name in experiment.stimuli}
    clamped.update({name: False for name in experiment.inhibitors})
    for node, value in clamped.items():
        if node in index:
            initial[index[node]] = value
    dynamic_targets = tuple(
        sorted(set(model.rules).intersection(nodes).difference(clamped))
    )
    return nodes, index, tuple(initial), clamped, dynamic_targets


def asynchronous_lts(
    model: BooleanModel,
    experiment: Experiment,
    interface: Sequence[str] = INTERFACE,
    hidden_initial: bool = False,
    max_states: int = 50_000,
) -> cbm.LTS:
    """Construct a finite unitary-asynchronous LTS for one held-out condition.

    Measured time-zero interface values initialize observables.  Other relevant
    nodes use the declared hidden-value sensitivity (all zero by default).
    Stimuli and inhibitors are clamped throughout.  Updates outside the declared
    interface are hidden as tau.
    """
    nodes, index, initial_state, _clamped, dynamic_targets = _conditioned_initial_state(
        model, experiment, interface, hidden_initial
    )
    states = [initial_state]
    state_index = {initial_state: 0}
    edges = set()
    queue = deque([initial_state])
    interface_set = set(interface)

    while queue:
        state = queue.popleft()
        values = dict(zip(nodes, state))
        for target in dynamic_targets:
            desired = _evaluate(model.rules[target], values)
            position = index[target]
            if desired == state[position]:
                continue
            successor = list(state)
            successor[position] = desired
            successor_tuple = tuple(successor)
            if successor_tuple not in state_index:
                state_index[successor_tuple] = len(states)
                states.append(successor_tuple)
                queue.append(successor_tuple)
                if len(states) > max_states:
                    raise ValueError(
                        f"State limit exceeded for {model.name}/{experiment.cell_line}; "
                        "revise the declared interface or abstraction."
                    )
            label = f"{target}={int(desired)}" if target in interface_set else cbm.TAU
            edges.add((state_index[state], label, state_index[successor_tuple]))

    return cbm.LTS(
        name=f"{model.name}:{experiment.cell_line}",
        states=["".join("1" if value else "0" for value in state) for state in states],
        init=0,
        edges=sorted(edges),
    )


def synchronous_lts(
    model: BooleanModel,
    experiment: Experiment,
    interface: Sequence[str] = INTERFACE,
    hidden_initial: bool = False,
    max_states: int = 50_000,
) -> cbm.LTS:
    """Construct a global synchronous LTS as a declared semantic stress test.

    All unstable targets are evaluated from the current state and updated in
    one step.  The label is the sorted set of changed interface readouts; a
    hidden-only update is tau.  The asynchronous system remains the primary
    model because CASPOTS used asynchronous trajectories.
    """
    nodes, index, initial_state, _clamped, dynamic_targets = _conditioned_initial_state(
        model, experiment, interface, hidden_initial
    )
    states = [initial_state]
    state_index = {initial_state: 0}
    edges = set()
    queue = deque([initial_state])
    interface_set = set(interface)

    while queue:
        state = queue.popleft()
        values = dict(zip(nodes, state))
        successor = list(state)
        observable_changes = []
        changed = False
        for target in dynamic_targets:
            desired = _evaluate(model.rules[target], values)
            position = index[target]
            if desired == state[position]:
                continue
            changed = True
            successor[position] = desired
            if target in interface_set:
                observable_changes.append(f"{target}={int(desired)}")
        if not changed:
            continue
        successor_tuple = tuple(successor)
        if successor_tuple not in state_index:
            state_index[successor_tuple] = len(states)
            states.append(successor_tuple)
            queue.append(successor_tuple)
            if len(states) > max_states:
                raise ValueError(
                    f"State limit exceeded for synchronous {model.name}/"
                    f"{experiment.cell_line}."
                )
        label = (
            "sync[" + "|".join(sorted(observable_changes)) + "]"
            if observable_changes
            else cbm.TAU
        )
        edges.add((state_index[state], label, state_index[successor_tuple]))

    return cbm.LTS(
        name=f"{model.name}:{experiment.cell_line}:synchronous",
        states=["".join("1" if value else "0" for value in state) for state in states],
        init=0,
        edges=sorted(edges),
    )


def experimental_rmse(
    left: Experiment,
    right: Experiment,
    interface: Sequence[str] = INTERFACE,
) -> Tuple[float, int, Tuple[int, ...]]:
    common_times = tuple(
        time for time in sorted(set(left.observations) & set(right.observations))
        if time > 0
    )
    squared = []
    for time in common_times:
        for node in interface:
            if node in left.observations[time] and node in right.observations[time]:
                squared.append(
                    (left.observations[time][node] - right.observations[time][node]) ** 2
                )
    if not squared:
        raise ValueError("No common post-zero held-out observations for experimental RMSE")
    return math.sqrt(statistics.fmean(squared)), len(squared), common_times


def _formal_class(weak: bool, left_by_right: bool, right_by_left: bool) -> str:
    if weak:
        return "weak_bisimulation"
    if left_by_right and right_by_left:
        return "mutual_simulation"
    if left_by_right or right_by_left:
        return "one_way_simulation"
    return "not_comparable"


def _relation_direction(weak: bool, left_by_right: bool, right_by_left: bool) -> str:
    """Preserve the orientation that the aggregate formal class omits."""
    if weak:
        return "weak_bisimulation"
    if left_by_right and right_by_left:
        return "mutual_simulation"
    if left_by_right:
        return "left_simulated_by_right"
    if right_by_left:
        return "right_simulated_by_left"
    return "no_simulation_relation"


def validation_rows(
    use_mcrl2: bool = True,
    hidden_initial: bool = False,
    semantics: str = "asynchronous",
) -> List[Dict[str, object]]:
    verify_artifacts()
    medoids = {cell: select_medoid(cell) for cell in CELLS}
    models = {cell: model_from_medoid(medoids[cell]) for cell in CELLS}
    rows = []
    for condition in COMMON_CONDITIONS:
        experiments = {cell: get_experiment(cell, condition) for cell in CELLS}
        if semantics == "asynchronous":
            builder = asynchronous_lts
        elif semantics == "synchronous":
            builder = synchronous_lts
        else:
            raise ValueError(f"Unsupported update semantics: {semantics}")
        systems = {
            cell: builder(models[cell], experiments[cell], hidden_initial=hidden_initial)
            for cell in CELLS
        }
        for left, right in itertools.combinations(CELLS, 2):
            lts_left, lts_right = systems[left], systems[right]
            strong = cbm.strong_bisimilar(lts_left, lts_right)
            weak = cbm.weak_bisimilar(lts_left, lts_right)
            left_by_right = cbm.weak_simulates(lts_left, lts_right)
            right_by_left = cbm.weak_simulates(lts_right, lts_left)
            distance = cbm.behavioural_distance(lts_left, lts_right, k=6)
            graphlet_similarity = mb.lts_graphlet_similarity(lts_left, lts_right)
            empirical, n_values, times = experimental_rmse(
                experiments[left], experiments[right]
            )
            oracle = (
                pv.compare_with_mcrl2(lts_left, lts_right)
                if use_mcrl2
                else {
                    "mcrl2_strong_bisimilar": None,
                    "mcrl2_weak_bisimilar": None,
                    "mcrl2_weak_trace_equivalent": None,
                }
            )
            rows.append(
                {
                    "condition": condition.name,
                    "left_cell": left,
                    "right_cell": right,
                    "interface_size": len(INTERFACE),
                    "common_times": ";".join(map(str, times)),
                    "experimental_values": n_values,
                    "experimental_rmse": empirical,
                    "clause_jaccard": _jaccard(medoids[left].clauses, medoids[right].clauses),
                    "left_states": len(lts_left.states),
                    "right_states": len(lts_right.states),
                    "left_edges": len(lts_left.edges),
                    "right_edges": len(lts_right.edges),
                    "strong_bisimilar": strong,
                    "weak_bisimilar": weak,
                    "left_simulated_by_right": left_by_right,
                    "right_simulated_by_left": right_by_left,
                    "formal_class": _formal_class(weak, left_by_right, right_by_left),
                    "relation_direction": _relation_direction(
                        weak, left_by_right, right_by_left
                    ),
                    "trace_distance_k6": distance,
                    "lts_gda_similarity": graphlet_similarity,
                    "hidden_initial_value": int(hidden_initial),
                    "update_semantics": semantics,
                    **oracle,
                    "python_mcrl2_strong_agree": (
                        strong == oracle["mcrl2_strong_bisimilar"] if use_mcrl2 else None
                    ),
                    "python_mcrl2_weak_agree": (
                        weak == oracle["mcrl2_weak_bisimilar"] if use_mcrl2 else None
                    ),
                }
            )
    return rows


def semantic_sensitivity_rows() -> List[Dict[str, object]]:
    """Pair asynchronous and synchronous outcomes for the nine HPN comparisons."""
    asynchronous = validation_rows(use_mcrl2=False, semantics="asynchronous")
    synchronous = validation_rows(use_mcrl2=False, semantics="synchronous")
    key = lambda row: (row["condition"], row["left_cell"], row["right_cell"])
    sync_by_key = {key(row): row for row in synchronous}
    rows = []
    for primary in asynchronous:
        stress = sync_by_key[key(primary)]
        rows.append(
            {
                "condition": primary["condition"],
                "left_cell": primary["left_cell"],
                "right_cell": primary["right_cell"],
                "asynchronous_class": primary["formal_class"],
                "synchronous_class": stress["formal_class"],
                "class_preserved": primary["formal_class"] == stress["formal_class"],
                "asynchronous_trace_distance_k6": primary["trace_distance_k6"],
                "synchronous_trace_distance_k6": stress["trace_distance_k6"],
                "asynchronous_lts_gda_similarity": primary["lts_gda_similarity"],
                "synchronous_lts_gda_similarity": stress["lts_gda_similarity"],
                "asynchronous_left_states": primary["left_states"],
                "asynchronous_right_states": primary["right_states"],
                "synchronous_left_states": stress["left_states"],
                "synchronous_right_states": stress["right_states"],
            }
        )
    return rows


def _ranks(values: Sequence[float]) -> List[float]:
    ordered = sorted((value, index) for index, value in enumerate(values))
    ranks = [0.0] * len(values)
    cursor = 0
    while cursor < len(ordered):
        end = cursor + 1
        while end < len(ordered) and ordered[end][0] == ordered[cursor][0]:
            end += 1
        rank = (cursor + 1 + end) / 2
        for _, index in ordered[cursor:end]:
            ranks[index] = rank
        cursor = end
    return ranks


def _correlation(left: Sequence[float], right: Sequence[float]) -> float:
    mean_left, mean_right = statistics.fmean(left), statistics.fmean(right)
    numerator = sum((a - mean_left) * (b - mean_right) for a, b in zip(left, right))
    denominator = math.sqrt(
        sum((a - mean_left) ** 2 for a in left)
        * sum((b - mean_right) ** 2 for b in right)
    )
    return numerator / denominator if denominator else 0.0


def spearman(left: Sequence[float], right: Sequence[float]) -> float:
    return _correlation(_ranks(left), _ranks(right))


def concordance_test(rows: Sequence[Mapping[str, object]]) -> Dict[str, object]:
    """Exploratory metric/data concordance without ordinalising relations.

    Formal relation classes are nominal and one-way simulation is directional,
    so no scalar class encoding or class/RMSE inferential test is performed.
    Predeclared continuous trace and LTS-GDA diagnostics retain their exact,
    condition-stratified permutation tests.
    """
    grouped = []
    for condition in (item.name for item in COMMON_CONDITIONS):
        group = [row for row in rows if row["condition"] == condition]
        grouped.append(group)
    trace_distance = [
        float(row["trace_distance_k6"]) for group in grouped for row in group
    ]
    graphlet_distance = [
        1.0 - float(row["lts_gda_similarity"]) for group in grouped for row in group
    ]
    empirical_groups = [
        [float(row["experimental_rmse"]) for row in group] for group in grouped
    ]
    empirical = [value for group in empirical_groups for value in group]
    observed_trace = spearman(trace_distance, empirical)
    observed_graphlet = spearman(graphlet_distance, empirical)
    null_trace = []
    null_graphlet = []
    permutations = [list(itertools.permutations(group)) for group in empirical_groups]
    for combination in itertools.product(*permutations):
        permuted = [value for group in combination for value in group]
        null_trace.append(spearman(trace_distance, permuted))
        null_graphlet.append(spearman(graphlet_distance, permuted))
    p_trace = sum(value >= observed_trace - 1e-12 for value in null_trace) / len(null_trace)
    p_graphlet = sum(
        value >= observed_graphlet - 1e-12 for value in null_graphlet
    ) / len(null_graphlet)
    relation_order = (
        "weak_bisimulation",
        "mutual_simulation",
        "one_way_simulation",
        "not_comparable",
    )
    formal_class_summary = {}
    for relation in relation_order:
        values = [
            float(row["experimental_rmse"])
            for row in rows
            if str(row["formal_class"]) == relation
        ]
        if values:
            formal_class_summary[relation] = {
                "n": len(values),
                "rmse_min": min(values),
                "rmse_median": statistics.median(values),
                "rmse_max": max(values),
            }

    direction_order = (
        "weak_bisimulation",
        "mutual_simulation",
        "left_simulated_by_right",
        "right_simulated_by_left",
        "no_simulation_relation",
    )
    direction_summary = {}
    for direction in direction_order:
        values = [
            float(row["experimental_rmse"])
            for row in rows
            if str(
                row.get(
                    "relation_direction",
                    _relation_direction(
                        bool(row["weak_bisimilar"]),
                        bool(row["left_simulated_by_right"]),
                        bool(row["right_simulated_by_left"]),
                    ),
                )
            )
            == direction
        ]
        if values:
            direction_summary[direction] = {
                "n": len(values),
                "rmse_min": min(values),
                "rmse_median": statistics.median(values),
                "rmse_max": max(values),
            }

    return {
        "n_model_pair_conditions": len(rows),
        "n_conditions": len(grouped),
        "formal_relation_analysis": "nominal and direction-preserving descriptive summary",
        "formal_class_scalar_encoding_used": False,
        "formal_class_inferential_test_performed": False,
        "reason_no_formal_class_inference": (
            "n=9 is too small and directional simulation classes do not define a "
            "biologically justified one-dimensional order"
        ),
        "formal_class_rmse_summary": formal_class_summary,
        "relation_direction_rmse_summary": direction_summary,
        "trace_distance_spearman_rho": observed_trace,
        "trace_distance_exact_permutation_p_one_sided": p_trace,
        "graphlet_distance_spearman_rho": observed_graphlet,
        "graphlet_distance_exact_permutation_p_one_sided": p_graphlet,
        "null_permutations": len(null_trace),
        "continuous_formal_diagnostic": "weak observable trace Jaccard distance at k=6",
        "structural_baseline_metric": "one minus LTS-GDA similarity",
        "experimental_metric": "RMSE over common post-zero held-out values",
    }


def initial_state_sensitivity_rows() -> List[Dict[str, object]]:
    """Report state-space growth for the extreme all-one hidden initialization.

    Exact cross-model relations are deliberately not attempted for this stress
    condition: candidate relation matrices would contain hundreds of millions
    of pairs.  The table makes that tractability boundary explicit.
    """
    medoids = {cell: select_medoid(cell) for cell in CELLS}
    models = {cell: model_from_medoid(medoids[cell]) for cell in CELLS}
    rows = []
    for condition in COMMON_CONDITIONS:
        for cell in CELLS:
            experiment = get_experiment(cell, condition)
            primary = asynchronous_lts(models[cell], experiment, hidden_initial=False)
            stress = asynchronous_lts(models[cell], experiment, hidden_initial=True)
            rows.append(
                {
                    "condition": condition.name,
                    "cell_line": cell,
                    "primary_hidden_initial": 0,
                    "stress_hidden_initial": 1,
                    "primary_states": len(primary.states),
                    "primary_edges": len(primary.edges),
                    "stress_states": len(stress.states),
                    "stress_edges": len(stress.edges),
                    "state_growth_factor": len(stress.states) / len(primary.states),
                    "exact_cross_model_relation_attempted": False,
                    "reason": "stress state-pair matrix exceeds declared exact-analysis budget",
                }
            )
    return rows


def write_results(use_mcrl2: bool = True) -> Tuple[Path, Path, Path, Path, Path]:
    RESULTS.mkdir(parents=True, exist_ok=True)
    medoid_path = RESULTS / "hpn_dream_medoids.csv"
    rows_path = RESULTS / "hpn_dream_formal_data_validation.csv"
    sensitivity_path = RESULTS / "hpn_dream_initial_state_sensitivity.csv"
    statistics_path = RESULTS / "hpn_dream_concordance.json"
    semantics_path = RESULTS / "hpn_dream_semantic_sensitivity.csv"

    medoid_rows = medoid_summary()
    rows = validation_rows(use_mcrl2=use_mcrl2, hidden_initial=False)
    sensitivity = initial_state_sensitivity_rows()
    semantics = semantic_sensitivity_rows()
    stats = concordance_test(rows)

    for path, data in (
        (medoid_path, medoid_rows),
        (rows_path, rows),
        (sensitivity_path, sensitivity),
        (semantics_path, semantics),
    ):
        with path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(
                handle, fieldnames=list(data[0]), lineterminator="\n"
            )
            writer.writeheader()
            writer.writerows(data)
    statistics_path.write_text(json.dumps(stats, indent=2) + "\n", encoding="utf-8")
    return medoid_path, rows_path, sensitivity_path, statistics_path, semantics_path


def main() -> None:
    paths = write_results(use_mcrl2=True)
    rows = validation_rows(use_mcrl2=False)
    print("HPN-DREAM medoids:")
    for row in medoid_summary():
        print(
            f"  {row['cell_line']}: row {row['medoid_row_zero_based']}, "
            f"{row['active_clauses']} clauses / {row['family_size']} models"
        )
    print("Concordance:", json.dumps(concordance_test(rows), indent=2))
    print("Wrote:", ", ".join(str(path.relative_to(ROOT)) for path in paths))


if __name__ == "__main__":
    main()
