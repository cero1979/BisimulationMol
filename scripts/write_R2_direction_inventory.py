"""Index directional statements and join them to the verified R2 pair audit."""
from pathlib import Path
import csv
import json
import re

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "revision_R2"
PATTERN = re.compile(r"preceq|weakpre|strongsim|weaksim|simulat|bisim|contain|one.way|mutual|not comparable|non.compar|trace.equal|trace.equiv", re.I)


def main():
    records = json.loads((ROOT / "results/direction_audit_R2.json").read_text())
    assert all(row["independent_oracle_agrees"] for row in records)
    paths = [ROOT/"README.md", ROOT/"REPRODUCIBILITY.md",
             OUT/"main_jbcb_R2.tex", OUT/"Supplementary_Validation_R2.tex"]
    for directory, globs in [("src", ["*.py"]), ("tests", ["*.py"]), ("results", ["*.csv", "*.json", "*.tex"])]:
        for pattern in globs:
            paths.extend(sorted((ROOT/directory).glob(pattern)))
    paths += [ROOT/"make_figures.py", ROOT/"scripts/make_revision_R2_figures.py",
              ROOT/"scripts/update_notebook_netmahib.py"]
    inventory = []
    for path in paths:
        for number, line in enumerate(path.read_text(errors="replace").splitlines(), 1):
            if PATTERN.search(line):
                inventory.append({"path": str(path.relative_to(ROOT)), "location": f"line {number}", "text": line.strip()})
    nb = json.loads((ROOT/"notebooks/metodologia_multiescala.ipynb").read_text())
    for i, cell in enumerate(nb["cells"]):
        for number, line in enumerate("".join(cell.get("source", [])).splitlines(), 1):
            if PATTERN.search(line):
                inventory.append({"path": "notebooks/metodologia_multiescala.ipynb",
                                  "location": f"cell {i}, line {number}", "text": line.strip()})
        for j, output in enumerate(cell.get("outputs", [])):
            text = "".join(output.get("text", [])) or "".join(output.get("data", {}).get("text/plain", []))
            for number, line in enumerate(text.splitlines(), 1):
                if PATTERN.search(line):
                    inventory.append({"path": "notebooks/metodologia_multiescala.ipynb",
                                      "location": f"cell {i}, output {j}, line {number}", "text": line.strip()})
    with (OUT/"direction_statement_inventory.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["path", "location", "text"], lineterminator="\n")
        writer.writeheader(); writer.writerows(inventory)
    report = """# Formal Direction Audit: R2

Convention: left <=_w right means **right simulates left**.
Production weak_simulates(left,right), the new independent game, the manuscript
definition, and machine-readable fields use this same orientation.

The statement inventory covers current R2 source/captions, source modules,
result CSV/JSON/TeX files, tests, README, reproducibility guide and notebook
source plus rendered textual outputs. Historical journal manuscripts and the
immutable R1 archive are not rewritten. Older scripts/functions retain compatible
names; their parameter roles are documented and checked against primitive
predicates. An occurrence inventory is a navigation aid, not a proof that
arbitrary prose was automatically verified.

## Audited locations and roles

| Statement/location | Mathematical relation | Expected orientation | Computed/independent check | Status and action |
|---|---|---|---|---|
| Definition 4, Section 3.3 | L1 <= L2 | right simulates left | raw-edge game agrees with production | Retained, clarified |
| Example 1, Appendix A | early <= late only | candidate in reference | exact relation certificate and mCRL2 on tau-free inputs | Retained; expanded proof |
| Proposition 2 and Table 5 | strong => weak => mutual => equal traces | each converse has a distinct witness | three independently checked constructions | Retained; witness roles explicit |
| Synthetic Table S1 and Figure S1 | added branch: reference <= candidate; early choice: candidate <= reference | left=reference, right=candidate | six class and primitive-predicate checks | No reclassification |
| GIM Table 2/Figure 2 | A/B both directions; C neither | left=animal, right=plant | regenerated interfaces and raw-edge oracle | No change |
| Curated Table 3 and RCD paragraph | plant <= animal only | right=plant, left=animal in audit | source compare_module and independent game | No change |
| HPN Section 6/Figure S2 | explicit left/right Booleans, nominal categories | alphabetical cell-pair order is preserved | all 18 asynchronous/synchronous pairs independently checked | No ordinal conversion |
| concurrent_biomodels.compare_module | plant_le_animal = weak_simulates(plant,animal) | animal is defender | unchanged outputs and regression tests | Correct |
| method_benchmark.classify_pair | reference_simulated_by_candidate | candidate is defender | swapped-order Example 1 test | Correct |
| HPN validation_rows | left_simulated_by_right | right is defender | direction-preserving tests and pair audit | Correct |
| README / REPRODUCIBILITY / notebook | same conditional GIM, RCD and HPN meanings | no inversion in public narrative | executed outputs match unchanged deterministic result tables | R2 context updated |

No mathematical or directional correction was discovered. The new ambiguity
removed is quantifier scope in Example 1, not a reversed result. The statement
that weak simulation implies trace inclusion is never used as its converse.

## Per-pair computed directions

All rows below have agreement on strong/weak bisimilarity and both simulations
with the independently implemented raw-edge game. For curated/GIM rows,
left=animal and right=plant. HPN row IDs give left/right cell order.

| Case | Left simulated by right | Right simulated by left | Weak bisimilar | Exact traces equal | Independent agreement |
|---|---|---|---|---|---|
"""
    for row in records:
        values = [row["case"]] + [str(row[key]) for key in
            ["left_simulated_by_right", "right_simulated_by_left", "weak_bisimilar", "exact_trace_equal", "independent_oracle_agrees"]]
        report += "| " + " | ".join(values) + " |\n"
    report += f"\nInventory: {len(inventory)} matched source/output lines in direction_statement_inventory.csv.\n"
    (OUT/"formal_direction_audit.md").write_text(report)
    text = (OUT/"main_jbcb_R2.tex").read_text()
    body = text.split(r"\section{Introduction}",1)[1].split(r"\appendix",1)[0]
    chunks = re.split(r"(?=\\section\{)", body)
    counts = []
    for chunk in chunks:
        title = re.search(r"\\section\{([^}]+)", chunk)
        title = title.group(1) if title else "Introduction"
        prose = re.sub(r"\\[A-Za-z]+\*?(?:\[[^]]*\])?", " ", chunk)
        counts.append({"section": title, "approximate_words_including_captions": len(prose.split())})
    (OUT/"main_text_space_audit.json").write_text(json.dumps(counts, indent=2)+"\n")
    print(f"Indexed {len(inventory)} directional lines and {len(records)} independently checked pairs.")


if __name__ == "__main__":
    main()
