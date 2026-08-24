"""Biologically predeclared observational-interface sensitivity for GIM."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Dict, List

try:
    from . import concurrent_biomodels as cbm
    from . import method_benchmark as mb
    from . import pn_gdda
except ImportError:  # Support direct execution through make_figures.py.
    import concurrent_biomodels as cbm  # type: ignore[no-redef]
    import method_benchmark as mb  # type: ignore[no-redef]
    import pn_gdda  # type: ignore[no-redef]

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"


def _formal_class(
    weak: bool,
    animal_simulated_by_plant: bool,
    plant_simulated_by_animal: bool,
) -> str:
    if weak:
        return "weak_bisimulation"
    if animal_simulated_by_plant and plant_simulated_by_animal:
        return "mutual_simulation"
    if animal_simulated_by_plant:
        return "animal_simulated_by_plant"
    if plant_simulated_by_animal:
        return "plant_simulated_by_animal"
    return "not_comparable"


def _internal_transitions(net: cbm.PetriNet) -> str:
    return ";".join(sorted(t.name for t in net.transitions if t.label == cbm.TAU))


def _result_interpretation(interface_id: str, formal_class: str) -> str:
    if formal_class == "weak_bisimulation" and interface_id == "A":
        return (
            "The encoded models match the high-level detection-checkpoint-repair-"
            "recovery/exit control structure after internal relays are hidden."
        )
    if formal_class == "weak_bisimulation" and interface_id == "B":
        return (
            "The relation survives separation of damage, signalling, and repair "
            "channels while terminal mechanisms remain collapsed."
        )
    if formal_class == "not_comparable" and interface_id == "C":
        return (
            "The relation breaks when apoptosis and the encoded plant SMR/"
            "differentiation-endoreduplication sequence become distinct readouts."
        )
    return f"Executed relation under interface {interface_id}: {formal_class}."


def analysis_rows(k: int = 6) -> List[Dict[str, object]]:
    """Execute the three predeclared interfaces on unchanged GIM structures."""
    base_animal, base_plant = cbm.ddr_animal(), cbm.ddr_plant()
    structural_592 = pn_gdda.pn_gdda_similarity(
        base_animal, base_plant, holmes_compatible=True
    )
    structural_576 = pn_gdda.pn_gdda_similarity(
        base_animal, base_plant, holmes_compatible=False
    )
    rows: List[Dict[str, object]] = []
    for interface_id, specification in cbm.GIM_INTERFACE_SPECS.items():
        animal, plant = cbm.gim_models_for_interface(interface_id)
        animal_lts, plant_lts = animal.reachability_lts(), plant.reachability_lts()
        strong = cbm.strong_bisimilar(animal_lts, plant_lts)
        weak = cbm.weak_bisimilar(animal_lts, plant_lts)
        animal_by_plant = cbm.weak_simulates(animal_lts, plant_lts)
        plant_by_animal = cbm.weak_simulates(plant_lts, animal_lts)
        formal_class = _formal_class(weak, animal_by_plant, plant_by_animal)
        distance = cbm.behavioural_distance(animal_lts, plant_lts, k=k)
        rows.append(
            {
                "interface_id": interface_id,
                "interface_name": specification["name"],
                "biological_question": specification["biological_question"],
                "predeclared_biological_rationale": specification["rationale"],
                "observable_labels": ";".join(
                    sorted(animal_lts.observables | plant_lts.observables)
                ),
                "animal_internal_transitions": _internal_transitions(animal),
                "plant_internal_transitions": _internal_transitions(plant),
                "animal_model_states": len(animal_lts.states),
                "plant_model_states": len(plant_lts.states),
                "strong_bisimulation": strong,
                "weak_bisimulation": weak,
                "animal_simulated_by_plant": animal_by_plant,
                "plant_simulated_by_animal": plant_by_animal,
                "formal_class": formal_class,
                f"trace_distance_k{k}": distance,
                f"trace_equivalent_at_k{k}": distance == 0.0,
                "pn_gdda_592_similarity": structural_592,
                "pn_gdda_576_similarity": structural_576,
                "lts_gda_similarity": mb.lts_graphlet_similarity(animal_lts, plant_lts),
                "result_interpretation": _result_interpretation(
                    interface_id, formal_class
                ),
                "literature_reference_keys": specification["literature_keys"],
                "structure_changed_between_interfaces": False,
            }
        )
    return rows


def _write_csv(path: Path, rows: List[Dict[str, object]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def _tex_escape(value: object) -> str:
    text = str(value)
    for source, target in (
        ("\\", "\\textbackslash{}"),
        ("_", "\\_"),
        ("&", "\\&"),
        ("%", "\\%"),
        ("#", "\\#"),
    ):
        text = text.replace(source, target)
    return text


def write_outputs() -> tuple[Path, Path, Path]:
    """Write interface results and the biological-justification audit."""
    RESULTS.mkdir(parents=True, exist_ok=True)
    sensitivity_path = RESULTS / "gim_interface_sensitivity.csv"
    justification_path = RESULTS / "gim_interface_justification.csv"
    justification_tex_path = RESULTS / "gim_interface_justification.tex"
    _write_csv(sensitivity_path, analysis_rows(k=6))
    _write_csv(justification_path, cbm.GIM_INTERFACE_JUSTIFICATION)
    with justification_tex_path.open("w", encoding="utf-8") as handle:
        handle.write("\\begin{tabularx}{\\textwidth}{@{}p{0.15\\textwidth}YYYp{0.15\\textwidth}@{}}\n")
        handle.write("\\toprule\n")
        handle.write(
            "Process & Animal/human & \\textit{Arabidopsis} & "
            "Interface rationale & Support \\\\" + "\n"
        )
        handle.write("\\colrule\n")
        for row in cbm.GIM_INTERFACE_JUSTIFICATION:
            interface_reason = f"{row['interface_status']}. {row['biological_reason']}"
            handle.write(
                " & ".join(
                    _tex_escape(value)
                    for value in (
                        row["event_process"],
                        row["animal_human_interpretation"],
                        row["arabidopsis_interpretation"],
                        interface_reason,
                        row["literature_support"],
                    )
                )
                + " \\\\" + "\n"
            )
        handle.write("\\botrule\n\\end{tabularx}\n")
    return sensitivity_path, justification_path, justification_tex_path


def main() -> None:
    paths = write_outputs()
    for row in analysis_rows():
        print(
            row["interface_id"],
            row["formal_class"],
            f"d6={row['trace_distance_k6']:.6f}",
            f"PN-GDDA={row['pn_gdda_592_similarity']:.6f}",
        )
    print("Wrote:", ", ".join(str(path.relative_to(ROOT)) for path in paths))


if __name__ == "__main__":
    main()
