"""External mCRL2 checks, including simulation on the tau-free Example 1."""
from pathlib import Path
import json
import re
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src import public_validation as pv
from src import formal_audit as audit


def main():
    binary = pv.find_ltscompare()
    rows = []
    for key, left, right in audit.hierarchy_pairs():
        production = audit.pair_audit(key, left, right)
        external = pv.compare_with_mcrl2(left, right, binary)
        row = {"case": key, "mcrl2_version": pv.mcrl2_version(binary), **external,
               "strong_agrees": external["mcrl2_strong_bisimilar"] == production["strong_bisimilar"],
               "weak_agrees": external["mcrl2_weak_bisimilar"] == production["weak_bisimilar"],
               "exact_trace_agrees": external["mcrl2_weak_trace_equivalent"] == production["exact_trace_equal"]}
        if all(label != "tau" for lts in (left, right) for _, label, _ in lts.edges):
            with tempfile.TemporaryDirectory() as directory:
                a, b = Path(directory)/"left.aut", Path(directory)/"right.aut"
                pv.write_aut(left, a); pv.write_aut(right, b)
                for field, p, q in [("left_simulated_by_right", a, b), ("right_simulated_by_left", b, a)]:
                    command = [str(binary), "--preorder=sim", "--in1=aut", "--in2=aut", str(p), str(q)]
                    result = subprocess.run(command, check=True, text=True, capture_output=True)
                    values = re.findall(r"^(true|false)$", result.stdout + result.stderr, re.MULTILINE)
                    if len(values) != 1:
                        raise RuntimeError(result.stdout + result.stderr)
                    row["mcrl2_" + field] = values[0] == "true"
                    row[field + "_agrees"] = row["mcrl2_" + field] == production[field]
                row["simulation_scope"] = "Strong simulation equals weak simulation here because both inputs are tau-free"
        assert all(value for name, value in row.items() if name.endswith("_agrees"))
        rows.append(row)
    path = ROOT / "results/mcrl2_hierarchy.json"
    path.write_text(json.dumps(rows, indent=2) + "\n")
    print(json.dumps(rows, indent=2))


if __name__ == "__main__":
    main()
