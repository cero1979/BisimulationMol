"""Independent formal and public-model validation.

This module adds two evidence layers that do not depend on the hand-curated
Arabidopsis/animal case study:

* exact comparison of exported LTSs with the independent ``ltscompare`` tool
  from mCRL2; and
* asynchronous state-transition systems generated from published GINsim
  models distributed as SBML-qual or GINML.

The public-model tests are deliberately model-level controls.  An exact copy,
a silent refinement and an observable-label perturbation have predeclared
equivalence outcomes.  They validate import and comparison behaviour on
externally authored network dynamics; they do not independently validate the
biological claims of the original models.
"""

from __future__ import annotations

import glob
import hashlib
import os
import random
import re
import shutil
import subprocess
import tempfile
import xml.etree.ElementTree as ET
import zipfile
from collections import deque
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Dict, Iterable, List, Mapping, Sequence, Tuple

try:  # Package import (tests and external users).
    from . import concurrent_biomodels as cbm
    from . import method_benchmark as mb
except ImportError:  # Script/notebook import with ``src`` on sys.path.
    import concurrent_biomodels as cbm
    import method_benchmark as mb


ROOT = Path(__file__).resolve().parents[1]
PUBLIC_MODEL_DIR = ROOT / "data" / "public_models"


@dataclass(frozen=True)
class PublicModelSource:
    key: str
    title: str
    format: str
    filename: str
    url: str
    sha256: str
    publication_doi: str
    repository_page: str
    initial_condition: str

    @property
    def path(self) -> Path:
        return PUBLIC_MODEL_DIR / self.filename


PUBLIC_MODEL_SOURCES: Tuple[PublicModelSource, ...] = (
    PublicModelSource(
        key="mammalian_cell_cycle",
        title="Mammalian cell-cycle regulation",
        format="SBML-qual",
        filename="Traynard_Boolean_MamCC_Apr2016.sbml",
        url=(
            "https://ginsim.github.io/models/2016-mammal-cell-cycle/"
            "Traynard_Boolean_MamCC_Apr2016.sbml"
        ),
        sha256="105eb2d1b44532762632245537315396c4deb912f1e1754b70edf2bdf2d9f02e",
        publication_doi="10.1093/bioinformatics/btw457",
        repository_page="https://ginsim.github.io/models/2016-mammal-cell-cycle/",
        initial_condition="CycD=1; all other components=0",
    ),
    PublicModelSource(
        key="p53_mdm2",
        title="p53-Mdm2 DNA-damage response",
        format="GINML",
        filename="p53Mdm2_tutorial_5march2018.zginml",
        url=(
            "https://ginsim.github.io/models/2009-mammal-p53-mdm2/"
            "p53Mdm2_tutorial_5march2018.zginml"
        ),
        sha256="511a7b0f7764ca88efbbe38fb6fe28d89a7080d34bc2fc5277b3c750026b6d81",
        publication_doi="10.1016/j.jtbi.2009.02.005",
        repository_page="https://ginsim.github.io/models/2009-mammal-p53-mdm2/",
        initial_condition="GINsim stored state 'damage'",
    ),
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_public_model_files() -> None:
    """Fail if a source file is absent or differs from the declared release."""
    for source in PUBLIC_MODEL_SOURCES:
        if not source.path.is_file():
            raise FileNotFoundError(
                f"Missing public model {source.path}. Run "
                "'python scripts/fetch_public_models.py'."
            )
        actual = sha256_file(source.path)
        if actual != source.sha256:
            raise ValueError(
                f"SHA-256 mismatch for {source.filename}: {actual} != {source.sha256}"
            )


Rule = Callable[[Mapping[str, int]], int]
Predicate = Callable[[Mapping[str, int]], bool]


@dataclass
class LogicalModel:
    name: str
    variables: Tuple[str, ...]
    max_levels: Dict[str, int]
    constants: frozenset[str]
    rules: Dict[str, Rule]
    initial: Tuple[int, ...]
    source: PublicModelSource

    def asynchronous_lts(self, max_states: int = 100_000) -> cbm.LTS:
        """Generate the standard unitary asynchronous transition system.

        At each transition one non-constant component moves by one level toward
        its logical target.  Labels expose the updated component and direction.
        """
        if max_states < 1:
            raise ValueError("max_states must be positive")

        index = {self.initial: 0}
        states = [self.initial]
        queue = deque([self.initial])
        edges = set()

        while queue:
            state = queue.popleft()
            values = dict(zip(self.variables, state))
            for position, variable in enumerate(self.variables):
                if variable in self.constants or variable not in self.rules:
                    continue
                target = int(self.rules[variable](values))
                current = state[position]
                if not 0 <= target <= self.max_levels[variable]:
                    raise ValueError(
                        f"Rule for {variable} returned invalid level {target}"
                    )
                if target == current:
                    continue
                direction = 1 if target > current else -1
                updated = list(state)
                updated[position] += direction
                successor = tuple(updated)
                if successor not in index:
                    if len(states) >= max_states:
                        raise ValueError(
                            f"State cap {max_states} reached for public model {self.name}"
                        )
                    index[successor] = len(states)
                    states.append(successor)
                    queue.append(successor)
                label = f"{variable}_{'up' if direction > 0 else 'down'}"
                edges.add((index[state], label, index[successor]))

        labels = [
            ",".join(f"{name}={level}" for name, level in zip(self.variables, state))
            for state in states
        ]
        return cbm.LTS(self.name, labels, 0, sorted(edges))


def _local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _attribute(element: ET.Element, name: str, default: str | None = None) -> str:
    for key, value in element.attrib.items():
        if _local(key) == name:
            return value
    if default is not None:
        return default
    raise ValueError(f"Element {_local(element.tag)} lacks attribute {name}")


def _compile_mathml(element: ET.Element) -> Callable[[Mapping[str, int]], object]:
    kind = _local(element.tag)
    if kind == "math":
        children = list(element)
        if len(children) != 1:
            raise ValueError("MathML <math> must contain one expression")
        return _compile_mathml(children[0])
    if kind == "ci":
        variable = (element.text or "").strip()
        return lambda values, variable=variable: values[variable]
    if kind == "cn":
        value = int((element.text or "0").strip())
        return lambda _values, value=value: value
    if kind != "apply":
        raise ValueError(f"Unsupported MathML element: {kind}")

    children = list(element)
    if not children:
        raise ValueError("Empty MathML apply expression")
    operator = _local(children[0].tag)
    arguments = [_compile_mathml(child) for child in children[1:]]

    if operator == "and":
        return lambda values: all(bool(arg(values)) for arg in arguments)
    if operator == "or":
        return lambda values: any(bool(arg(values)) for arg in arguments)
    if operator == "not":
        if len(arguments) != 1:
            raise ValueError("MathML not expects one argument")
        return lambda values: not bool(arguments[0](values))

    comparisons = {
        "eq": lambda a, b: a == b,
        "neq": lambda a, b: a != b,
        "lt": lambda a, b: a < b,
        "leq": lambda a, b: a <= b,
        "gt": lambda a, b: a > b,
        "geq": lambda a, b: a >= b,
    }
    if operator in comparisons:
        if len(arguments) != 2:
            raise ValueError(f"MathML {operator} expects two arguments")
        compare = comparisons[operator]
        return lambda values: compare(arguments[0](values), arguments[1](values))
    raise ValueError(f"Unsupported MathML operator: {operator}")


def load_sbml_qual(source: PublicModelSource) -> LogicalModel:
    root = ET.parse(source.path).getroot()
    species = [element for element in root.iter() if _local(element.tag) == "qualitativeSpecies"]
    variables = tuple(_attribute(element, "id") for element in species)
    max_levels = {
        _attribute(element, "id"): int(_attribute(element, "maxLevel", "1"))
        for element in species
    }
    constants = frozenset(
        _attribute(element, "id")
        for element in species
        if _attribute(element, "constant", "false").lower() == "true"
    )

    rules: Dict[str, Rule] = {}
    for transition in (element for element in root.iter() if _local(element.tag) == "transition"):
        outputs = [element for element in transition.iter() if _local(element.tag) == "output"]
        if len(outputs) != 1:
            raise ValueError("Only single-output SBML-qual transitions are supported")
        variable = _attribute(outputs[0], "qualitativeSpecies")
        default_terms = [
            element for element in transition.iter() if _local(element.tag) == "defaultTerm"
        ]
        default_level = int(_attribute(default_terms[0], "resultLevel", "0"))
        terms: List[Tuple[int, Predicate]] = []
        for term in (
            element for element in transition.iter() if _local(element.tag) == "functionTerm"
        ):
            math = next(
                (element for element in term.iter() if _local(element.tag) == "math"),
                None,
            )
            if math is None:
                raise ValueError(f"Function term for {variable} has no MathML condition")
            terms.append((int(_attribute(term, "resultLevel")), _compile_mathml(math)))

        def rule(
            values: Mapping[str, int],
            terms: Sequence[Tuple[int, Predicate]] = tuple(terms),
            default_level: int = default_level,
        ) -> int:
            for level, predicate in terms:
                if bool(predicate(values)):
                    return level
            return default_level

        rules[variable] = rule

    initial_values = {variable: 0 for variable in variables}
    initial_values["CycD"] = 1
    initial = tuple(initial_values[variable] for variable in variables)
    return LogicalModel(
        source.title,
        variables,
        max_levels,
        constants,
        rules,
        initial,
        source,
    )


_GIN_TOKEN = re.compile(r"\s*([A-Za-z_][A-Za-z0-9_.-]*(?::\d+)?|[!&|()])")


class _GinExpressionParser:
    def __init__(self, expression: str):
        self.expression = expression
        self.tokens: List[str] = []
        position = 0
        while position < len(expression):
            match = _GIN_TOKEN.match(expression, position)
            if not match:
                raise ValueError(f"Unsupported GINML expression near: {expression[position:]}")
            self.tokens.append(match.group(1))
            position = match.end()
        self.position = 0

    def parse(self) -> Predicate:
        predicate = self._parse_or()
        if self.position != len(self.tokens):
            raise ValueError(f"Unexpected token {self.tokens[self.position]}")
        return predicate

    def _peek(self, token: str) -> bool:
        return self.position < len(self.tokens) and self.tokens[self.position] == token

    def _take(self) -> str:
        if self.position >= len(self.tokens):
            raise ValueError("Unexpected end of GINML expression")
        token = self.tokens[self.position]
        self.position += 1
        return token

    def _parse_or(self) -> Predicate:
        terms = [self._parse_and()]
        while self._peek("|"):
            self._take()
            terms.append(self._parse_and())
        return lambda values: any(term(values) for term in terms)

    def _parse_and(self) -> Predicate:
        terms = [self._parse_not()]
        while self._peek("&"):
            self._take()
            terms.append(self._parse_not())
        return lambda values: all(term(values) for term in terms)

    def _parse_not(self) -> Predicate:
        if self._peek("!"):
            self._take()
            operand = self._parse_not()
            return lambda values: not operand(values)
        return self._parse_atom()

    def _parse_atom(self) -> Predicate:
        if self._peek("("):
            self._take()
            predicate = self._parse_or()
            if not self._peek(")"):
                raise ValueError("Missing closing parenthesis in GINML expression")
            self._take()
            return predicate
        token = self._take()
        if token in {"!", "&", "|", "(", ")"}:
            raise ValueError(f"Expected component, found {token}")
        if ":" in token:
            variable, raw_level = token.rsplit(":", 1)
            level = int(raw_level)
            return lambda values, variable=variable, level=level: values[variable] == level
        return lambda values, variable=token: values[variable] > 0


def load_ginml(source: PublicModelSource) -> LogicalModel:
    with zipfile.ZipFile(source.path) as archive:
        graph_name = next(
            name for name in archive.namelist() if name.endswith("regulatoryGraph.ginml")
        )
        root = ET.fromstring(archive.read(graph_name))
        initial_name = next(
            name for name in archive.namelist() if name.endswith("initialState")
        )
        initial_root = ET.fromstring(archive.read(initial_name))

    graph = next(element for element in root.iter() if _local(element.tag) == "graph")
    node_order = graph.attrib.get("nodeorder", "").split()
    nodes = {
        element.attrib["id"]: element
        for element in graph
        if _local(element.tag) == "node"
    }
    variables = tuple(node_order or nodes.keys())
    max_levels = {variable: int(nodes[variable].attrib.get("maxvalue", "1")) for variable in variables}
    constants = frozenset(
        variable for variable in variables if nodes[variable].attrib.get("input") == "true"
    )

    rules: Dict[str, Rule] = {}
    for variable in variables:
        terms = []
        for value in (child for child in nodes[variable] if _local(child.tag) == "value"):
            level = int(value.attrib["val"])
            expression = next(
                child.attrib["str"] for child in value if _local(child.tag) == "exp"
            )
            terms.append((level, _GinExpressionParser(expression).parse()))
        terms.sort(key=lambda item: item[0], reverse=True)

        def rule(
            values: Mapping[str, int],
            terms: Sequence[Tuple[int, Predicate]] = tuple(terms),
        ) -> int:
            for level, predicate in terms:
                if predicate(values):
                    return level
            return 0

        rules[variable] = rule

    stored_states = [element for element in initial_root.iter() if _local(element.tag) == "initialState"]
    selected = next(
        (element for element in stored_states if element.attrib.get("name") == "damage"),
        stored_states[0],
    )
    initial_values = {variable: 0 for variable in variables}
    for assignment in selected.attrib.get("value", "").split():
        variable, raw_level = assignment.split(";", 1)
        initial_values[variable] = int(raw_level)
    initial = tuple(initial_values[variable] for variable in variables)
    return LogicalModel(
        source.title,
        variables,
        max_levels,
        constants,
        rules,
        initial,
        source,
    )


def load_public_model(source: PublicModelSource) -> LogicalModel:
    if source.format == "SBML-qual":
        return load_sbml_qual(source)
    if source.format == "GINML":
        return load_ginml(source)
    raise ValueError(f"Unsupported public model format: {source.format}")


def public_model_lts() -> Dict[str, Tuple[LogicalModel, cbm.LTS]]:
    verify_public_model_files()
    result = {}
    for source in PUBLIC_MODEL_SOURCES:
        model = load_public_model(source)
        result[source.key] = (model, model.asynchronous_lts())
    return result


def _clone_lts(lts: cbm.LTS, name: str) -> cbm.LTS:
    return cbm.LTS(name, list(lts.states), lts.init, list(lts.edges))


@dataclass(frozen=True)
class PublicValidationCase:
    model: LogicalModel
    case: str
    reference: cbm.LTS
    candidate: cbm.LTS
    expected_strong: bool
    expected_weak: bool
    expected_weak_trace: bool


def public_validation_cases() -> List[PublicValidationCase]:
    cases: List[PublicValidationCase] = []
    for offset, (_key, (model, base)) in enumerate(public_model_lts().items()):
        exact = _clone_lts(base, base.name + "-exact-copy")
        refined = cbm.refine_with_tau(
            base,
            random.Random(101 + offset),
            min(5, max(1, len(base.edges))),
        )
        perturb_label = sorted(base.observables)[0]
        perturbed = cbm.relabel_observable(
            base, perturb_label, perturb_label + "_perturbed"
        )
        cases.extend(
            [
                PublicValidationCase(model, "exact copy", base, exact, True, True, True),
                PublicValidationCase(
                    model, "silent refinement", base, refined, False, True, True
                ),
                PublicValidationCase(
                    model, "observable perturbation", base, perturbed, False, False, False
                ),
            ]
        )
    return cases


def _aut_quote(label: str) -> str:
    return label.replace("\\", "\\\\").replace('"', '\\"')


def write_aut(lts: cbm.LTS, path: Path) -> None:
    """Export an LTS in the Aldebaran AUT format accepted by mCRL2."""
    edges = sorted(set(lts.edges))
    lines = [f"des ({lts.init},{len(edges)},{len(lts.states)})"]
    lines.extend(f'({source},"{_aut_quote(label)}",{target})' for source, label, target in edges)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def find_ltscompare(required: bool = True) -> Path | None:
    configured = os.environ.get("MCRL2_LTSCOMPARE")
    candidates: List[str] = [configured] if configured else []
    discovered = shutil.which("ltscompare")
    if discovered:
        candidates.append(discovered)
    candidates.extend(
        [
            "/Applications/mCRL2.app/Contents/bin/ltscompare",
            *glob.glob("/Volumes/mcrl2*/mCRL2.app/Contents/bin/ltscompare"),
        ]
    )
    for candidate in candidates:
        if candidate and Path(candidate).is_file() and os.access(candidate, os.X_OK):
            return Path(candidate)
    if required:
        raise FileNotFoundError(
            "ltscompare was not found. Install mCRL2 or set MCRL2_LTSCOMPARE."
        )
    return None


def mcrl2_version(binary: Path | None = None) -> str:
    executable = binary or find_ltscompare(required=True)
    completed = subprocess.run(
        [str(executable), "--version"],
        check=True,
        text=True,
        capture_output=True,
    )
    first_line = (completed.stdout or completed.stderr).splitlines()[0]
    return first_line.strip()


def _mcrl2_equivalent(
    binary: Path,
    reference_path: Path,
    candidate_path: Path,
    equivalence: str,
) -> bool:
    completed = subprocess.run(
        [
            str(binary),
            f"--equivalence={equivalence}",
            "--in1=aut",
            "--in2=aut",
            "--tau=tau",
            str(reference_path),
            str(candidate_path),
        ],
        check=True,
        text=True,
        capture_output=True,
    )
    matches = re.findall(r"^(true|false)$", completed.stdout, flags=re.MULTILINE)
    if not matches:
        matches = re.findall(
            r"^(true|false)$", completed.stderr, flags=re.MULTILINE
        )
    if not matches:
        raise RuntimeError(
            "Could not parse ltscompare output:\n"
            + completed.stdout
            + completed.stderr
        )
    return matches[-1] == "true"


def compare_with_mcrl2(
    reference: cbm.LTS,
    candidate: cbm.LTS,
    binary: Path | None = None,
) -> Dict[str, bool]:
    executable = binary or find_ltscompare(required=True)
    with tempfile.TemporaryDirectory(prefix="bisimulationmol-aut-") as directory:
        directory_path = Path(directory)
        reference_path = directory_path / "reference.aut"
        candidate_path = directory_path / "candidate.aut"
        write_aut(reference, reference_path)
        write_aut(candidate, candidate_path)
        return {
            "mcrl2_strong_bisimilar": _mcrl2_equivalent(
                executable, reference_path, candidate_path, "bisim"
            ),
            "mcrl2_weak_bisimilar": _mcrl2_equivalent(
                executable, reference_path, candidate_path, "weak-bisim"
            ),
            "mcrl2_weak_trace_equivalent": _mcrl2_equivalent(
                executable, reference_path, candidate_path, "weak-trace"
            ),
        }


def public_model_summary() -> List[Dict[str, object]]:
    rows = []
    for key, (model, lts) in public_model_lts().items():
        rows.append(
            {
                "model": key,
                "title": model.source.title,
                "format": model.source.format,
                "variables": len(model.variables),
                "theoretical_state_space": _product(
                    level + 1 for level in model.max_levels.values()
                ),
                "reachable_states": len(lts.states),
                "reachable_edges": len(lts.edges),
                "initial_condition": model.source.initial_condition,
                "publication_doi": model.source.publication_doi,
                "repository_page": model.source.repository_page,
                "source_file": model.source.filename,
                "sha256": model.source.sha256,
            }
        )
    return rows


def _product(values: Iterable[int]) -> int:
    result = 1
    for value in values:
        result *= value
    return result


def run_public_validation(binary: Path | None = None) -> List[Dict[str, object]]:
    executable = binary or find_ltscompare(required=True)
    version = mcrl2_version(executable)
    rows = []
    for case in public_validation_cases():
        python_strong = cbm.strong_bisimilar(case.reference, case.candidate)
        python_weak = cbm.weak_bisimilar(case.reference, case.candidate)
        oracle = compare_with_mcrl2(case.reference, case.candidate, executable)
        expected_match = (
            python_strong == case.expected_strong
            and python_weak == case.expected_weak
            and oracle["mcrl2_strong_bisimilar"] == case.expected_strong
            and oracle["mcrl2_weak_bisimilar"] == case.expected_weak
            and oracle["mcrl2_weak_trace_equivalent"] == case.expected_weak_trace
        )
        rows.append(
            {
                "model": case.model.source.key,
                "case": case.case,
                "expected_strong": case.expected_strong,
                "expected_weak": case.expected_weak,
                "expected_weak_trace": case.expected_weak_trace,
                "python_strong_bisimilar": python_strong,
                "python_weak_bisimilar": python_weak,
                **oracle,
                "python_mcrl2_strong_agree": (
                    python_strong == oracle["mcrl2_strong_bisimilar"]
                ),
                "python_mcrl2_weak_agree": (
                    python_weak == oracle["mcrl2_weak_bisimilar"]
                ),
                "all_expected_results_match": expected_match,
                "n_states_reference": len(case.reference.states),
                "n_states_candidate": len(case.candidate.states),
                "n_edges_reference": len(case.reference.edges),
                "n_edges_candidate": len(case.candidate.edges),
                "mcrl2_version": version,
                "source_sha256": case.model.source.sha256,
            }
        )
    return rows


_SYNTHETIC_WEAK_TRACE_EXPECTED = {
    "identity": True,
    "silent refinement": True,
    "label mismatch": False,
    "label order swap": False,
    "added branch": False,
    "trace-equivalent branching": True,
}


def run_synthetic_mcrl2_validation(binary: Path | None = None) -> List[Dict[str, object]]:
    executable = binary or find_ltscompare(required=True)
    version = mcrl2_version(executable)
    rows = []
    for case in mb.synthetic_cases(n_steps=12, seed=17):
        python_strong = cbm.strong_bisimilar(case.reference, case.candidate)
        python_weak = cbm.weak_bisimilar(case.reference, case.candidate)
        oracle = compare_with_mcrl2(case.reference, case.candidate, executable)
        rows.append(
            {
                "case": case.case,
                "python_strong_bisimilar": python_strong,
                "python_weak_bisimilar": python_weak,
                **oracle,
                "python_mcrl2_strong_agree": (
                    python_strong == oracle["mcrl2_strong_bisimilar"]
                ),
                "python_mcrl2_weak_agree": (
                    python_weak == oracle["mcrl2_weak_bisimilar"]
                ),
                "mcrl2_trace_matches_predeclared": (
                    oracle["mcrl2_weak_trace_equivalent"]
                    == _SYNTHETIC_WEAK_TRACE_EXPECTED[case.case]
                ),
                "mcrl2_version": version,
            }
        )
    return rows


if __name__ == "__main__":
    print(mcrl2_version())
    print("\nPublic models")
    for row in public_model_summary():
        print(
            f"{row['model']:<24} variables={row['variables']:<3} "
            f"states={row['reachable_states']:<5} edges={row['reachable_edges']}"
        )
    print("\nPublic-model controls")
    for row in run_public_validation():
        print(
            f"{row['model']:<24} {row['case']:<24} "
            f"strong={row['python_strong_bisimilar']} "
            f"weak={row['python_weak_bisimilar']} "
            f"oracle_agreement={row['python_mcrl2_weak_agree']}"
        )
