"""Compare results with HEAD, excluding only declared run-dependent metrics."""

import json
from pathlib import Path
import subprocess


RESOURCE_PATHS = {
    "results/death_receptor_sustained_trace_equivalence.json": [()],
    "results/death_receptor_withdrawal_trace_equivalence.json": [()],
    "results/death_receptor_sustained_comparison.json": [("trace_analysis",)],
    "results/death_receptor_withdrawal_comparison.json": [("trace_analysis",)],
    "results/death_receptor_trace_equivalence.json": [("sustained",), ("withdrawal",)],
}
COUNTERS = ("subset_product_states", "stored_subset_bytes")


def comparison_bytes(name, payload):
    if name not in RESOURCE_PATHS:
        return payload
    data = json.loads(payload)
    for path in RESOURCE_PATHS[name]:
        record = data
        for key in path:
            if not isinstance(record, dict) or key not in record:
                raise ValueError(f"{name}: missing trace-analysis record {path}")
            record = record[key]
        if not isinstance(record, dict):
            raise ValueError(f"{name}: invalid trace-analysis record {path}")
        for key in COUNTERS:
            value = record.pop(key, None)
            if type(value) is not int or value < 0:
                raise ValueError(f"{name}: invalid or missing {key}")
    return json.dumps(data, sort_keys=True, separators=(",", ":")).encode()


def results_equal(name, expected, actual):
    return comparison_bytes(name, expected) == comparison_bytes(name, actual)


def main():
    root = Path.cwd()
    names = subprocess.check_output(
        ["git", "ls-files", "-z", "--", "results"], cwd=root
    ).decode().split("\0")
    names = [name for name in names if name and name != "results/scalability_runtime.csv"]
    if not names:
        raise SystemExit("No tracked results found; run from the repository root.")
    failures = []
    for name in names:
        expected = subprocess.check_output(["git", "show", "HEAD:" + name], cwd=root)
        try:
            equal = results_equal(name, expected, (root / name).read_bytes())
        except (OSError, ValueError) as error:
            failures.append(f"{name}: {error}")
        else:
            if not equal:
                failures.append(name)
    if failures:
        raise SystemExit("Scientific result differences:\n" + "\n".join(failures))
    print(f"OK: {len(names)} tracked result files match HEAD; only scalability timings "
          "and the two declared subset-search progress counters are excluded.")


if __name__ == "__main__":
    main()
