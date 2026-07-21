#!/usr/bin/env python3
"""Deterministic CASPOTS scoring of blind HPN-DREAM model representatives.

CASPOTS 0.3 returns the first yielded Clingo model in ``ASPSolver.sample``.
During optimization that model need not be final, which makes the published
``mse`` command dependent on solver enumeration.  This runner keeps the same
primary weighted-threshold objective, consumes the solve handle to completion,
and adds deterministic secondary objectives: continuous squared error and then
the source-family row index.  Every score is repeated and equality is required.

The three structure-only medoids are scored against each held-out cell line.
Native-family oracle scores are also reported, but are explicitly retrospective
because they select a family member using the test response.
"""

from __future__ import annotations

import argparse
import contextlib
import csv
import hashlib
import importlib.metadata
import io
import itertools
import json
import math
import platform
import statistics
import sys
import tempfile
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src import hpn_dream_validation as hpn  # noqa: E402


SECONDARY_OBJECTIVES = r"""
#program deterministic_score.
#minimize { SQ@1,E,T,S : measured(E,T,S,0), guessed(E,T,S,1),
                           obs(E,T,S,M), SQ=(100-M)*(100-M) }.
#minimize { SQ@1,E,T,S : measured(E,T,S,1), guessed(E,T,S,0),
                           obs(E,T,S,M), SQ=M*M }.
#minimize { I@0 : model(I) }.
"""


def _require_optional_dependencies():
    try:
        import caspo  # noqa: F401
        import caspots  # noqa: F401
        import clingo  # noqa: F401
    except ImportError as error:
        raise SystemExit(
            "CASPOTS validation dependencies are missing. Create the pinned "
            "environment with 'conda env create -f environment-hpn.yml'."
        ) from error


def _normalize_test_header(source: Path, destination: Path) -> None:
    """Normalize the historical MCF7 uppercase inhibitor suffix for CASPOTS."""
    with source.open(newline="", encoding="utf-8-sig") as handle:
        rows = list(csv.reader(handle))
    rows[0] = [
        "TR:mTOR_pS2448i" if name == "TR:mTOR_pS2448I" else name
        for name in rows[0]
    ]
    with destination.open("w", newline="", encoding="utf-8") as handle:
        csv.writer(handle, lineterminator="\n").writerows(rows)


def _write_medoid(cell_line: str, destination: Path) -> None:
    header, models = hpn.load_family(cell_line)
    medoid = hpn.select_medoid(cell_line)
    active = set(models[medoid.row_index])
    with destination.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(header)
        writer.writerow([int(name in active) for name in header])


def _rmse_from_atoms(atoms, factor: float = 100.0) -> tuple[float, float, int]:
    observations = {}
    measured = {}
    guessed = {}
    for atom in atoms:
        if atom.name not in {"obs", "measured", "guessed"} or len(atom.arguments) != 4:
            continue
        experiment, timepoint, node, value = atom.arguments
        key = (experiment.number, timepoint.number, str(node))
        if atom.name == "obs":
            observations[key] = value.number / factor
        elif atom.name == "measured":
            measured[key] = value.number
        else:
            guessed[key] = value.number
    keys = sorted(set(observations) & set(measured) & set(guessed))
    if not keys:
        raise RuntimeError("CASPOTS optimum contains no scored observations")
    discrete = math.sqrt(
        sum((observations[key] - measured[key]) ** 2 for key in keys) / len(keys)
    )
    model = math.sqrt(
        sum((observations[key] - guessed[key]) ** 2 for key in keys) / len(keys)
    )
    return discrete, model, len(keys)


def _solve_score(pkn_path: Path, test_path: Path, networks_path: Path) -> dict:
    from caspo.core import LogicalNetworkList
    from clingo import Number

    from caspots import identify
    from caspots.asputils import funset
    from caspots.console import read_dataset, read_pkn
    from caspots.networks import domain_of_networks

    options = identify.SolverOptions(
        pkn=str(pkn_path),
        dataset=str(test_path),
        networks=str(networks_path),
        family="all",
        factor=100,
    )
    with contextlib.redirect_stdout(io.StringIO()):
        graph, hypergraph = read_pkn(options)
        dataset = read_dataset(options, graph)
        networks = LogicalNetworkList.from_csv(str(networks_path))
        termset = funset(hypergraph, dataset)

    with tempfile.NamedTemporaryFile("w", suffix=".lp", delete=False) as handle:
        domain_path = Path(handle.name)
        handle.write(domain_of_networks(networks, hypergraph, dataset))

    try:
        solver = identify.ASPSolver(termset, options, domain=str(domain_path))
        with contextlib.redirect_stdout(io.StringIO()):
            control, parts = solver.default_control()
        control.add("deterministic_score", [], SECONDARY_OBJECTIVES)
        parts.append(("minimize_weight", []))
        parts.append(("deterministic_score", []))
        control.ground(parts)
        control.configuration.solve.models = 1
        control.configuration.solve.opt_mode = "optN"

        final_atoms = None
        final_cost = None
        optimum_proven = False
        yielded_models = 0
        with control.solve(yield_=True) as solve_handle:
            for model in solve_handle:
                yielded_models += 1
                final_atoms = tuple(model.symbols(atoms=True))
                final_cost = tuple(model.cost)
                optimum_proven = bool(model.optimality_proven)
            solve_result = solve_handle.get()
        if final_atoms is None or not solve_result.satisfiable:
            raise RuntimeError(f"No CASPOTS solution for {networks_path.name}/{test_path.name}")

        discrete_rmse, model_rmse, observations = _rmse_from_atoms(final_atoms)
        selected = [
            atom.arguments[0].number
            for atom in final_atoms
            if atom.name == "model" and len(atom.arguments) == 1
        ]
        return {
            "discrete_rmse": discrete_rmse,
            "model_rmse": model_rmse,
            "excess_rmse": model_rmse - discrete_rmse,
            "scored_observations": observations,
            "primary_weight_cost": final_cost[0] if final_cost else None,
            "secondary_squared_error_cost": final_cost[1] if len(final_cost or ()) > 1 else None,
            "selected_network_zero_based": selected[0] if len(selected) == 1 else None,
            "yielded_optimization_models": yielded_models,
            "optimum_proven_on_final_yield": optimum_proven,
            "solve_search_exhausted": bool(solve_result.exhausted),
        }
    finally:
        domain_path.unlink(missing_ok=True)


def _score_repeated(
    pkn: Path,
    test: Path,
    networks: Path,
    repeats: int,
) -> dict:
    results = []
    elapsed = []
    for _ in range(repeats):
        started = time.perf_counter()
        results.append(_solve_score(pkn, test, networks))
        elapsed.append(time.perf_counter() - started)
    deterministic_fields = (
        "discrete_rmse",
        "model_rmse",
        "primary_weight_cost",
        "secondary_squared_error_cost",
        "selected_network_zero_based",
    )
    signatures = [tuple(result[field] for field in deterministic_fields) for result in results]
    if len(set(signatures)) != 1:
        raise RuntimeError(
            f"Non-deterministic CASPOTS optimum for {networks.name}/{test.name}: {signatures}"
        )
    result = dict(results[0])
    result["repeats"] = repeats
    result["deterministic_across_repeats"] = True
    result["median_runtime_seconds"] = sorted(elapsed)[len(elapsed) // 2]
    return result


def run(repeats: int = 2) -> list[dict]:
    _require_optional_dependencies()
    hpn.verify_artifacts()
    rows = []
    pkn = hpn.DATA / "merged_pkn.sif"
    with tempfile.TemporaryDirectory(prefix="bisimulationmol-hpn-") as directory:
        temporary = Path(directory)
        tests = {}
        medoids = {}
        for cell in hpn.CELLS:
            tests[cell] = temporary / f"{cell}_test_normalized.csv"
            _normalize_test_header(hpn.TEST_FILES[cell], tests[cell])
            medoids[cell] = temporary / f"{cell}_medoid.csv"
            _write_medoid(cell, medoids[cell])

        for source_cell in hpn.CELLS:
            for target_cell in hpn.CELLS:
                print(f"blind medoid {source_cell} -> held-out {target_cell}", flush=True)
                score = _score_repeated(
                    pkn, tests[target_cell], medoids[source_cell], repeats
                )
                rows.append(
                    {
                        "selection": "blind_structure_medoid",
                        "source_cell": source_cell,
                        "target_cell": target_cell,
                        "native_context": source_cell == target_cell,
                        "source_medoid_row_zero_based": hpn.select_medoid(source_cell).row_index,
                        **score,
                    }
                )

        for target_cell in hpn.CELLS:
            print(f"retrospective family oracle {target_cell}", flush=True)
            score = _score_repeated(
                pkn, tests[target_cell], hpn.FAMILY_FILES[target_cell], repeats
            )
            rows.append(
                {
                    "selection": "retrospective_family_oracle",
                    "source_cell": target_cell,
                    "target_cell": target_cell,
                    "native_context": True,
                    "source_medoid_row_zero_based": "",
                    **score,
                }
            )
    return rows


def summarize(rows: list[dict]) -> dict:
    blind = [row for row in rows if row["selection"] == "blind_structure_medoid"]
    advantages = []
    native_top_or_tied = 0
    details = []
    for target in hpn.CELLS:
        target_rows = [row for row in blind if row["target_cell"] == target]
        native = next(row for row in target_rows if row["source_cell"] == target)
        cross = [row for row in target_rows if row["source_cell"] != target]
        cross_mean = statistics.fmean(float(row["excess_rmse"]) for row in cross)
        advantage = cross_mean - float(native["excess_rmse"])
        advantages.append(advantage)
        top_or_tied = float(native["model_rmse"]) <= min(
            float(row["model_rmse"]) for row in target_rows
        ) + 1e-12
        native_top_or_tied += int(top_or_tied)
        details.append(
            {
                "target_cell": target,
                "native_excess_rmse": float(native["excess_rmse"]),
                "mean_cross_excess_rmse": cross_mean,
                "native_advantage": advantage,
                "native_top_or_tied": top_or_tied,
            }
        )
    observed = statistics.fmean(advantages)
    null = [
        statistics.fmean(sign * value for sign, value in zip(signs, advantages))
        for signs in itertools.product((-1, 1), repeat=len(advantages))
    ]
    p_value = sum(value >= observed - 1e-12 for value in null) / len(null)
    return {
        "n_target_cell_lines": len(hpn.CELLS),
        "native_top_or_tied": native_top_or_tied,
        "mean_native_advantage_excess_rmse": observed,
        "exact_paired_sign_permutation_p_one_sided": p_value,
        "sign_permutations": len(null),
        "interpretation": (
            "held-out compatibility is reproduced, but native-cell specificity "
            "is not established"
        ),
        "per_target": details,
    }


def _version(distribution: str) -> str:
    try:
        return importlib.metadata.version(distribution)
    except importlib.metadata.PackageNotFoundError:
        return "unknown"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repeats", type=int, default=2)
    parser.add_argument("--summarize-existing", action="store_true")
    args = parser.parse_args()
    if args.repeats < 2:
        parser.error("--repeats must be at least 2 for the determinism audit")

    hpn.RESULTS.mkdir(parents=True, exist_ok=True)
    csv_path = hpn.RESULTS / "hpn_dream_caspots_rmse.csv"
    if args.summarize_existing:
        with csv_path.open(newline="", encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))
    else:
        rows = run(args.repeats)
        with csv_path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(
                handle, fieldnames=list(rows[0]), lineterminator="\n"
            )
            writer.writeheader()
            writer.writerows(rows)

    source = Path(__file__).read_bytes()
    metadata = {
        "runner_sha256": hashlib.sha256(source).hexdigest(),
        "python": platform.python_version(),
        "caspo": _version("caspo"),
        "caspots": _version("caspots"),
        "clingo": _version("clingo"),
        "repeats": args.repeats,
        "all_scores_deterministic": all(
            str(row["deterministic_across_repeats"]).lower() == "true" for row in rows
        ),
        "historical_header_normalization": "TR:mTOR_pS2448I -> TR:mTOR_pS2448i for MCF7",
        "selection_warning": (
            "retrospective_family_oracle uses held-out response and is not a blind estimate"
        ),
    }
    metadata_path = hpn.RESULTS / "hpn_dream_caspots_metadata.json"
    metadata_path.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    summary_path = hpn.RESULTS / "hpn_dream_caspots_summary.json"
    summary_path.write_text(json.dumps(summarize(rows), indent=2) + "\n", encoding="utf-8")
    if not args.summarize_existing:
        print(f"Wrote {csv_path.relative_to(ROOT)}")
    print(f"Wrote {metadata_path.relative_to(ROOT)}")
    print(f"Wrote {summary_path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
