"""Apply the NetMAHIB benchmark section to the reproducibility notebook.

The transformation is idempotent: cells tagged ``netmahib-benchmark`` are
replaced on every run, while the existing biological case-study cells and their
outputs are preserved until the notebook is executed again.
"""

from pathlib import Path

import nbformat


ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK = ROOT / "notebooks" / "metodologia_multiescala.ipynb"
TAG = "netmahib-benchmark"


TITLE = """# Auditing observable behaviour in qualitative biological network models
### Reproducible method validation and an Arabidopsis-animal case study

This notebook executes the computational framework reported in the NetMAHIB
manuscript. The primary object of inference is a **pair of explicit qualitative
models under a declared observational interface**. Formal equivalence between
those models is not interpreted as organism-level or experimental biological
equivalence.

The notebook has two logically separate parts:

1. **Method validation independent of the biological case study.** Six synthetic
   model pairs have construction-level ground truth. Strong and weak results are
   cross-checked with mCRL2, and the import-to-comparison workflow is tested on
   two externally authored GINsim models: mammalian cell-cycle regulation and
   the p53--Mdm2 DNA-damage response. Three independently inferred HPN-DREAM
   model families are then fixed without test-value access and confronted with
   held-out mTOR-inhibitor phosphoproteomic responses. Weak bisimulation is also
   compared with trace equality, a transparent structural profile and LTS-GDA,
   a graphlet-degree/directed-motif baseline motivated by PN-GDDA. One-way
   simulation is independently checked by an attacker--defender game over every
   one- and two-state LTS on the declared audit alphabet. The HPN comparisons are
   also repeated under global synchronous updates.
2. **Illustrative biological case study.** Literature-curated plant and
   animal/human Petri nets are compared for selected cancer-relevant modules.
   These results describe the encoded models only and are reported conditionally
   on the chosen abstraction and interface.

Additional diagnostics audit transition provenance, interface sensitivity,
silent-refinement invariance, label-permutation nulls, seed sensitivity and trace
depth. All generated tables and figures are reproducible from the public
repository: <https://github.com/cero1979/BisimulationMol>.
"""


SUMMARY = """## Summary

- The independent synthetic suite recovers all six predeclared formal relations.
- The Python engine and mCRL2 202607.0 agree on all strong and weak decisions in
  the synthetic and public-model controls. Exact mCRL2 weak-trace outcomes also
  match every predeclared trace control.
- The independent weak-simulation game agrees on all 67,600 ordered pairs among
  the 260 LTSs with at most two states and labels in `{a, tau}`.
- The public mammalian cell-cycle and p53--Mdm2 models generate nontrivial
  asynchronous systems of 826 and 17 reachable states, respectively. Their
  controls validate the software path on external dynamics, not biological truth.
- Structure-only medoids from 72 BT20, 191 BT549 and 21 MCF7 public Boolean
  networks generate nine genuinely cross-model comparisons under shared held-out
  perturbations. Python and mCRL2 agree on all decisions: six pairs have one-way
  simulation and three are not comparable.
- CASPOTS held-out compatibility is reproduced deterministically, but native
  medoids rank first or tie in only two of three cell lines. Native specificity
  (p=0.25) and formal-class/data concordance (p=0.111) are not established.
- Weak bisimulation gives the correct binary equivalence decision in every case;
  trace equality scores 5/6, LTS-GDA 4/6 and the structural profile 3/6.
- Synchronous-update stress preserves seven of nine HPN formal classes; two
  one-way simulations become non-comparability. LTS-GDA distance has
  `rho=0.669` with held-out profile distance, but its exact `p=0.097` remains
  inconclusive.
- Runtime and candidate-relation size are reported explicitly; timings are
  machine-dependent, while all categorical outputs and model sizes are
  deterministic.
- In the illustrative case study, the **curated models** for `GIM`, `DCE` and
  `SPS` are weakly bisimilar under their declared interfaces; `RCD` is related by
  one-way simulation and `AID` is not comparable.
- These model-level results do not establish experimental equivalence between
  Arabidopsis and human biology. They identify conditional hypotheses and
  demonstrate how the software classifies explicit network models.

Regenerate the complete artifact from the project root with
`make external-validation && make figures && make test && make notebook`.
"""


def tagged(cell):
    return TAG in cell.get("metadata", {}).get("tags", [])


def tag(cell):
    cell.setdefault("metadata", {}).setdefault("tags", []).append(TAG)
    return cell


def main() -> None:
    nb = nbformat.read(NOTEBOOK, as_version=4)
    nb.cells = [cell for cell in nb.cells if not tagged(cell)]
    nb.cells[0].source = TITLE

    setup_index = next(
        i for i, cell in enumerate(nb.cells)
        if cell.cell_type == "code" and "import concurrent_biomodels as cbm" in cell.source
    )
    setup = nb.cells[setup_index]
    if "import method_benchmark as mb" not in setup.source:
        setup.source = setup.source.replace(
            "import concurrent_biomodels as cbm",
            "import concurrent_biomodels as cbm\nimport method_benchmark as mb",
        )
    if "import public_validation as pv" not in setup.source:
        setup.source = setup.source.replace(
            "import method_benchmark as mb",
            "import method_benchmark as mb\nimport public_validation as pv",
        )
    if "import hpn_dream_validation as hpn" not in setup.source:
        setup.source = setup.source.replace(
            "import public_validation as pv",
            "import public_validation as pv\nimport hpn_dream_validation as hpn",
        )
    if "import simulation_oracle as sim_oracle" not in setup.source:
        setup.source = setup.source.replace(
            "import hpn_dream_validation as hpn",
            "import hpn_dream_validation as hpn\nimport simulation_oracle as sim_oracle",
        )

    benchmark_cells = [
        tag(nbformat.v4.new_markdown_cell(
            """## Independent method validation

The suite below is generated without using any biological case-study model.
Each pair is constructed to instantiate a known relation, so the expected result
is fixed before the algorithms are run. The binary task asks whether a pair is
strongly or weakly equivalent; one-way simulations remain visible as a separate,
graded outcome."""
        )),
        tag(nbformat.v4.new_code_cell(
            """benchmark = pd.DataFrame(mb.validation_benchmark(n_steps=12, seed=17, k=8))
display(benchmark[[
    "case", "expected_class", "formal_class", "trace_distance",
    "lts_gda_similarity", "structural_similarity", "formal_match"
]])
assert benchmark["formal_match"].all()
print("OK: all six construction-level relations were recovered.")"""
        )),
        tag(nbformat.v4.new_markdown_cell(
            """### Comparison with non-formal baselines

The LTS-GDA baseline combines graphlet-degree-distribution agreement for all
connected induced graphlets through three nodes with directed labelled edge,
walk, divergence and convergence motifs. It is motivated by PN-GDDA but is not
presented as its 592-orbit Petri-net implementation. The simpler structural
profile averages state count, edge count, label multiset and out-degree
multiset. The trace baseline compares observable languages through depth eight.
These methods test complementary local, linear-time and branching-time views."""
        )),
        tag(nbformat.v4.new_code_cell(
            """baseline = pd.DataFrame(mb.baseline_accuracy(benchmark.to_dict("records")))
display(baseline)
assert float(baseline.loc[baseline["method"] == "weak bisimulation", "accuracy"].iloc[0]) == 1.0
assert benchmark.loc[
    benchmark["case"] == "trace-equivalent branching", "trace_equivalent_at_k"
].iloc[0]
assert benchmark.loc[
    benchmark["case"] == "label order swap", "structurally_equivalent_at_0_9"
].iloc[0]
assert float(baseline.loc[baseline["method"] == "LTS-GDA (>=0.9)", "accuracy"].iloc[0]) == 4 / 6
print("OK: the benchmark exposes the predeclared trace-only and structure-only failure cases.")"""
        )),
        tag(nbformat.v4.new_markdown_cell(
            """### Independent mCRL2 oracle and public models

Every LTS is exported in Aldebaran AUT format and checked by `ltscompare` from
mCRL2 202607.0. The comparison covers strong bisimulation, weak bisimulation
and exact weak-trace equivalence. One-way simulation is checked separately by a
dual attacker--defender least-fixed-point game on all 67,600 ordered pairs of
the 260 LTSs having at most two states over `{a, tau}`. The same import path is
then exercised on two public
GINsim models with source URLs and SHA-256 hashes fixed in the repository.

For each external model, an exact copy is a positive strong control, a silent
refinement is a weak-only positive control, and an observable-label perturbation
is a negative control. These transformations test importer and checker behaviour
on externally authored dynamics; they do not validate the model's biology."""
        )),
        tag(nbformat.v4.new_code_cell(
            """public_models = pd.DataFrame(pv.public_model_summary())
display(public_models[[
    "model", "format", "variables", "theoretical_state_space",
    "reachable_states", "reachable_edges", "initial_condition", "sha256"
]])

mcrl2_synthetic = pd.DataFrame(pv.run_synthetic_mcrl2_validation())
public_controls = pd.DataFrame(pv.run_public_validation())
public_semantics = pd.DataFrame(pv.public_semantic_sensitivity())
simulation_audit = sim_oracle.exhaustive_simulation_validation(max_states=2)
display(mcrl2_synthetic[[
    "case", "python_mcrl2_strong_agree", "python_mcrl2_weak_agree",
    "mcrl2_trace_matches_predeclared", "mcrl2_version"
]])
display(public_controls[[
    "model", "case", "expected_strong", "expected_weak",
    "python_strong_bisimilar", "python_weak_bisimilar",
    "mcrl2_strong_bisimilar", "mcrl2_weak_bisimilar",
    "mcrl2_weak_trace_equivalent", "all_expected_results_match"
]])
display(public_semantics)
display(pd.DataFrame([{k: v for k, v in simulation_audit.items() if k != "counterexamples"}]))

assert mcrl2_synthetic["python_mcrl2_strong_agree"].all()
assert mcrl2_synthetic["python_mcrl2_weak_agree"].all()
assert mcrl2_synthetic["mcrl2_trace_matches_predeclared"].all()
assert public_controls["all_expected_results_match"].all()
assert simulation_audit["complete_agreement"]
print("OK: mCRL2 and the exhaustive simulation-game oracle agree with every declared audit.")"""
        )),
        tag(nbformat.v4.new_markdown_cell(
            """### Blinded HPN-DREAM validation against held-out data

The public BT20, BT549 and MCF7 families were inferred from learning data by
Razzaq et al. A representative is selected solely from within-family clause
similarity; an anti-leakage test prevents this step from opening the held-out
files. The exact intersection of three mTOR-inhibitor conditions and seven
PI3K/MAPK/mTOR readouts defines the comparison before response values are used.

This is not another transformed control. The source models, cell contexts and
experimental profiles are genuinely distinct. A negative result is retained:
the analysis tests both held-out compatibility and whether native-cell models
outperform models inferred for other cell lines."""
        )),
        tag(nbformat.v4.new_code_cell(
            """import json

hpn_medoids = pd.DataFrame(hpn.medoid_summary())
hpn_formal = pd.DataFrame(hpn.validation_rows(use_mcrl2=True))
hpn_stats = hpn.concordance_test(hpn_formal.to_dict("records"))
hpn_semantics = pd.DataFrame(hpn.semantic_sensitivity_rows())
hpn_caspots = pd.read_csv(PROJECT_ROOT / "results" / "hpn_dream_caspots_rmse.csv")
with open(PROJECT_ROOT / "results" / "hpn_dream_caspots_summary.json") as handle:
    hpn_caspots_summary = json.load(handle)

display(hpn_medoids[[
    "cell_line", "family_size", "medoid_row_zero_based", "active_clauses",
    "mean_within_family_jaccard", "selection_uses_heldout_data"
]])
display(hpn_formal[[
    "condition", "left_cell", "right_cell", "left_states", "right_states",
    "formal_class", "experimental_rmse", "trace_distance_k6",
    "lts_gda_similarity",
    "python_mcrl2_strong_agree", "python_mcrl2_weak_agree"
]])
display(hpn_semantics)
display(hpn_caspots[hpn_caspots["selection"] == "blind_structure_medoid"][[
    "source_cell", "target_cell", "native_context", "discrete_rmse",
    "model_rmse", "excess_rmse", "deterministic_across_repeats"
]])
print("Exact class/data test:", hpn_stats)
print("Native specificity:", hpn_caspots_summary)

assert not hpn_medoids["selection_uses_heldout_data"].any()
assert hpn_formal["python_mcrl2_strong_agree"].all()
assert hpn_formal["python_mcrl2_weak_agree"].all()
assert not hpn_formal["weak_bisimilar"].any()
assert int(hpn_semantics["class_preserved"].sum()) == 7
assert hpn_caspots["deterministic_across_repeats"].all()
print("OK: independent models and held-out data were evaluated without test leakage.")"""
        )),
        tag(nbformat.v4.new_markdown_cell(
            """### Runtime scaling

Median wall-clock times are measured over three repetitions. They are expected
to vary by machine and load; the state counts, edge counts, candidate relation
sizes and formal outcomes are deterministic."""
        )),
        tag(nbformat.v4.new_code_cell(
            """scaling = pd.DataFrame(mb.scalability_benchmark(
    sizes=(8, 16, 32, 64, 96, 128), repeats=3, seed=23
))
display(scaling[[
    "n_steps", "variant", "n_states_reference", "n_states_candidate",
    "candidate_relation_pairs", "total_runtime_ms", "formal_class"
]])

fig, ax = plt.subplots(figsize=(7.2, 3.8))
for variant, group in scaling.groupby("variant", sort=False):
    ax.plot(group["candidate_relation_pairs"], group["total_runtime_ms"],
            marker="o", label=variant)
ax.set_xscale("log")
ax.set_yscale("log")
ax.set_xlabel(r"Candidate state pairs $|S_1||S_2|$")
ax.set_ylabel("Median total runtime (ms)")
ax.legend(frameon=False)
plt.show()"""
        )),
    ]
    nb.cells[setup_index + 1:setup_index + 1] = benchmark_cells

    summary_index = next(
        i for i, cell in reversed(list(enumerate(nb.cells)))
        if cell.cell_type == "markdown" and cell.source.lstrip().startswith("## Summary")
    )
    nb.cells[summary_index].source = SUMMARY
    nbformat.write(nb, NOTEBOOK)


if __name__ == "__main__":
    main()
