"""Apply the JBCB major-revision analyses to the reproducibility notebook.

The transformation is idempotent: cells tagged ``netmahib-benchmark`` are
replaced on every run, while the existing biological case-study cells and their
outputs are preserved until the notebook is executed again.
"""

from pathlib import Path

import nbformat


ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK = ROOT / "notebooks" / "metodologia_multiescala.ipynb"
TAG = "netmahib-benchmark"


TITLE = """# Locating resolution-dependent correspondence in DNA-damage response models
### JBCB second major revision: GIM first, formal verification as support

This notebook executes the computational framework reported in the revised JBCB
manuscript. The primary object of inference is a **pair of explicit qualitative
models under a declared observational interface**. Formal equivalence between
those models is not interpreted as organism-level or experimental biological
equivalence.

The principal result holds the animal/human and Arabidopsis Petri-net structures
fixed: PN-GDDA remains 0.9976, while recursive correspondence holds at interfaces
A/B and fails in both directions at C. This locates a boundary **within the three
declared interfaces**, not a unique minimal biological resolution. Known terminal
mechanisms motivate the interfaces; the computation does not discover those
differences or experimentally validate their consequences.

The notebook distinguishes two evidence layers (the GIM cells appear first):

1. **Formal/software verification independent of the biological case study.** Six synthetic
   model pairs have construction-level ground truth. Strong and weak results are
   cross-checked with mCRL2, and the import-to-comparison workflow is tested on
   two externally authored GINsim models: mammalian cell-cycle regulation and
   the p53--Mdm2 DNA-damage response. Three independently inferred HPN-DREAM
   model families are then fixed without test-value access and confronted with
   held-out mTOR-inhibitor phosphoproteomic responses. Weak bisimulation is also
   compared with trace equality, direct 151-graphlet/592-slot PN-GDDA, a
   transparent structural profile and labelled LTS-GDA. One-way
   simulation is independently checked by an attacker--defender game over every
   one- and two-state LTS on the declared audit alphabet. The HPN comparisons are
   also repeated under global synchronous updates.
2. **Central biological case study.** Three literature-motivated interfaces test
   where the encoded animal/human and Arabidopsis DNA-damage models retain or
   lose behavioral correspondence. Supporting curated modules remain secondary.
   Every result is conditional on the encoded models, semantics, and interface.

R2 adds explicit quantifier witnesses, failure certificates, independently
constructed weak targets, and exact trace inclusion without a depth cutoff.
Additional diagnostics audit transition provenance, interface sensitivity,
silent-refinement invariance, label-permutation nulls, seed sensitivity and trace
depth. All generated tables and figures are reproducible from the public
repository: <https://github.com/cero1979/BisimulationMol>.
"""


SUMMARY = """## Summary

- Central GIM result: fixed PN-GDDA 0.9976; weak bisimilarity at A/B; neither
  simulation direction at C. This is a conditional model/readout boundary.
- The second-round quantifier audit retains Example 1: early is simulated by
  late, not conversely, despite exact trace equality. All three hierarchy
  witnesses agree with independent computations; no false correction was made.
- The independent synthetic suite recovers all six predeclared formal relations.
- The Python engine and mCRL2 202607.0 agree on all strong and weak decisions in
  the synthetic and public-model controls. Exact mCRL2 weak-trace outcomes also
  match every predeclared trace control.
- The independent weak-simulation game agrees on all 67,600 ordered pairs among
  the 260 LTSs with at most two states and labels in `{a, tau}`.
- The public mammalian cell-cycle and p53--Mdm2 models generate nontrivial
  asynchronous systems of 826 and 17 reachable states, respectively. Their
  controls verify the software path on external dynamics, not biological truth.
- Structure-only medoids from 72 BT20, 191 BT549 and 21 MCF7 public Boolean
  networks generate nine genuinely cross-model comparisons under shared held-out
  perturbations. Python and mCRL2 agree on all decisions: six pairs have one-way
  simulation and three are not comparable.
- CASPOTS held-out compatibility is reproduced deterministically, but native
  medoids rank first or tie in only two of three cell lines. Native specificity
  remains unsupported (p=0.25). Formal relation classes are summarized
  nominally with direction preserved; no ordinal class test is used.
- Weak bisimulation gives the correct binary equivalence decision in every case;
  trace equality scores 5/6, LTS-GDA 4/6, the structural profile 3/6 and direct
  PN-GDDA 2/6. PN-GDDA calls all six pairs equivalent at the diagnostic 0.9
  threshold and cannot exceed 4/6 over any score cutoff.
- The generated 151-topology/592-slot catalog matches both inspected Holmes
  releases, and an independent four-node score matches Holmes 1.1.1 to 12
  decimal places. The 576-orbit automorphism sensitivity changes no decision.
- Synchronous-update stress preserves seven of nine HPN formal classes; two
  one-way simulations become non-comparability. LTS-GDA distance has
  `rho=0.669` with held-out profile distance, but its exact `p=0.097` remains
  inconclusive.
- Runtime and candidate-relation size are reported explicitly; timings are
  machine-dependent, while all categorical outputs and model sizes are
  deterministic.
- The unchanged GIM Petri-net structures score 0.9976 by PN-GDDA under all
  interfaces. Interfaces A (coarse) and B (pathway-level) are weakly bisimilar
  with d6=0, whereas interface C (terminal mechanism resolved) is not
  comparable with d6=0.352941.
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
    if "import gim_interface_analysis as gim" not in setup.source:
        setup.source = setup.source.replace(
            "import hpn_dream_validation as hpn",
            "import hpn_dream_validation as hpn\nimport gim_interface_analysis as gim",
        )
    if "import simulation_oracle as sim_oracle" not in setup.source:
        setup.source = setup.source.replace(
            "import hpn_dream_validation as hpn",
            "import hpn_dream_validation as hpn\nimport simulation_oracle as sim_oracle",
        )
    if "import pn_gdda as png" not in setup.source:
        setup.source = setup.source.replace(
            "import method_benchmark as mb",
            "import method_benchmark as mb\nimport pn_gdda as png",
        )

    benchmark_cells = [
        tag(nbformat.v4.new_markdown_cell(
            """## Independent formal/software verification

The suite below is generated without using any biological case-study model.
Each pair is constructed to instantiate a known relation, so the expected result
is fixed before the algorithms are run. The binary task asks whether a pair is
strongly or weakly equivalent; one-way simulations remain visible as separate,
direction-preserving outcomes. This is not biological validation."""
        )),
        tag(nbformat.v4.new_code_cell(
            """benchmark = pd.DataFrame(mb.validation_benchmark(n_steps=12, seed=17, k=8))
display(benchmark[[
    "case", "expected_class", "formal_class", "trace_distance",
    "pn_gdda_592_similarity", "pn_gdda_576_similarity",
    "lts_gda_similarity", "structural_similarity", "formal_match"
]])
assert benchmark["formal_match"].all()
print("OK: all six construction-level relations were recovered.")"""
        )),
        tag(nbformat.v4.new_markdown_cell(
            """### Comparison with non-formal baselines

PN-GDDA is evaluated directly using all 151 connected directed bipartite
graphlets through five nodes and the 592 orbit slots implemented by Holmes. Each
synthetic LTS is encoded canonically as a state-machine Petri net. LTS-GDA is a
separate label-aware reachable-state baseline combining four graphlet orbits
with directed labelled motifs. The simpler structural profile averages state
count, edge count, label multiset and out-degree multiset. The trace baseline
compares observable languages through depth eight. These methods test
complementary local, linear-time and branching-time views."""
        )),
        tag(nbformat.v4.new_code_cell(
            """baseline = pd.DataFrame(mb.baseline_accuracy(benchmark.to_dict("records")))
pn_thresholds = pd.DataFrame(
    mb.pn_gdda_threshold_sensitivity(benchmark.to_dict("records"))
)
display(baseline)
display(pn_thresholds)
assert float(baseline.loc[baseline["method"] == "weak bisimulation", "accuracy"].iloc[0]) == 1.0
assert benchmark.loc[
    benchmark["case"] == "trace-equivalent branching", "trace_equivalent_at_k"
].iloc[0]
assert benchmark.loc[
    benchmark["case"] == "label order swap", "structurally_equivalent_at_0_9"
].iloc[0]
assert float(baseline.loc[baseline["method"] == "LTS-GDA (>=0.9)", "accuracy"].iloc[0]) == 4 / 6
assert float(baseline.loc[baseline["method"] == "PN-GDDA-592 (>=0.9)", "accuracy"].iloc[0]) == 2 / 6
assert float(pn_thresholds["accuracy"].max()) == 4 / 6
print("OK: the benchmark exposes the predeclared trace-only and structure-only failure cases.")"""
        )),
        tag(nbformat.v4.new_markdown_cell(
            """### Direct PN-GDDA catalog and native-net audit

The published/Holmes 592-slot catalog is the primary comparator. A separate
type- and direction-preserving automorphism reconstruction yields 576 distinct
orbits and is retained as a sensitivity analysis. The four-node reference pair
below was also run independently in Holmes 1.1.1; `make holmes-pn-gdda` verifies
all 151 topology signatures and 592 root assignments from the official JAR.
The machine-readable record contains the JAR hash and both numerical scores. The five curated pairs are
then compared in their original Petri-net form rather than through reachable
LTS summaries."""
        )),
        tag(nbformat.v4.new_code_cell(
            """import json

pn_catalog = png.catalog_validation()
pn_native = pd.DataFrame(png.native_module_comparisons(k=6))
with open(PROJECT_ROOT / "results" / "holmes_pn_gdda_external_validation.json") as handle:
    holmes_external = json.load(handle)
display(pd.DataFrame(pn_catalog["published_holmes_catalog"]))
display(pd.DataFrame(pn_catalog["automorphism_partition_sensitivity"]))
display(pn_native[[
    "module", "pn_gdda_592_similarity", "pn_gdda_576_similarity",
    "pn_gdda_equivalent_at_0_9", "formal_class"
]])
print("Holmes reference:", pn_catalog["holmes_reference_score"])
print("Independent score:", pn_catalog["independent_python_score"])
print("External catalog audit:", holmes_external)

assert pn_catalog["published_graphlet_total"] == 151
assert pn_catalog["published_orbit_slot_total"] == 592
assert pn_catalog["automorphism_orbit_total"] == 576
assert pn_catalog["score_agreement_at_12_decimals"]
assert holmes_external["catalog_matches_python"]
assert holmes_external["holmes_graphlet_topologies"] == 151
assert holmes_external["holmes_catalog_slots_verified"] == 592
assert pn_native["pn_gdda_equivalent_at_0_9"].all()
assert (pn_native["catalog_sensitivity_delta"].abs() < 0.001).all()
print("OK: direct PN-GDDA is reproduced, externally checked and sensitivity-audited.")"""
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
            """### GIM as a biological observational-interface experiment

The animal/human and Arabidopsis Petri-net structures are held fixed. Three
literature-motivated interfaces are declared before interpreting the formal
outcomes: A observes shared functions, B separates damage, signalling and
repair channels, and C additionally distinguishes apoptosis from the encoded
plant SMR and terminal response. Thus any change below is caused by
observational resolution rather than topology."""
        )),
        tag(nbformat.v4.new_code_cell(
            """gim_output_paths = gim.write_outputs()
gim_interfaces = pd.DataFrame(gim.analysis_rows(k=6))
display(gim_interfaces[[
    "interface_id", "interface_name", "observable_labels",
    "animal_model_states", "plant_model_states",
    "animal_simulated_by_plant", "plant_simulated_by_animal",
    "formal_class", "trace_distance_k6", "pn_gdda_592_similarity"
]])

assert list(gim_interfaces["formal_class"]) == [
    "weak_bisimulation", "weak_bisimulation", "not_comparable"
]
assert np.allclose(gim_interfaces["trace_distance_k6"], [0.0, 0.0, 6 / 17])
assert gim_interfaces["pn_gdda_592_similarity"].nunique() == 1
assert not gim_interfaces["structure_changed_between_interfaces"].any()
assert all(path.exists() for path in gim_output_paths)
print("OK: unchanged structure, interface-dependent GIM behavioural result.")"""
        )),
        tag(nbformat.v4.new_markdown_cell(
            """### Exploratory HPN-DREAM check against held-out data

The public BT20, BT549 and MCF7 families were inferred from learning data by
Razzaq et al. A representative is selected solely from within-family clause
similarity; an anti-leakage test prevents this step from opening the held-out
files. The exact intersection of three mTOR-inhibitor conditions and seven
PI3K/MAPK/mTOR readouts defines the comparison before response values are used.

This is not another transformed control. The source models, cell contexts and
experimental profiles are genuinely distinct. The analysis remains exploratory.
Formal relations are nominal and one-way simulation is directional, so no
ordinal class score or class/RMSE inferential test is computed."""
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
    "formal_class", "relation_direction", "experimental_rmse", "trace_distance_k6",
    "lts_gda_similarity",
    "python_mcrl2_strong_agree", "python_mcrl2_weak_agree"
]])
display(hpn_semantics)
display(hpn_caspots[hpn_caspots["selection"] == "blind_structure_medoid"][[
    "source_cell", "target_cell", "native_context", "discrete_rmse",
    "model_rmse", "excess_rmse", "deterministic_across_repeats"
]])
print("Nominal relation/data summary and continuous diagnostics:", hpn_stats)
print("Native specificity:", hpn_caspots_summary)

assert not hpn_medoids["selection_uses_heldout_data"].any()
assert hpn_formal["python_mcrl2_strong_agree"].all()
assert hpn_formal["python_mcrl2_weak_agree"].all()
assert not hpn_formal["weak_bisimilar"].any()
assert not hpn_stats["formal_class_scalar_encoding_used"]
assert not hpn_stats["formal_class_inferential_test_performed"]
assert "formal_class_spearman_rho" not in hpn_stats
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
    gim_index = next(i for i, cell in enumerate(benchmark_cells)
                     if cell.cell_type == "markdown" and "### GIM as" in cell.source)
    gim_cells = benchmark_cells[gim_index:gim_index + 2]
    del benchmark_cells[gim_index:gim_index + 2]
    audit_cells = [
        tag(nbformat.v4.new_markdown_cell(
            """### R2 quantifier and direction audit

`left_simulated_by_right` means that the right system matches the left.
The oracle below builds weak targets from raw edges independently of production
helpers. Exact trace equality uses complete path enumeration for the acyclic
example and a finite subset-product algorithm without a depth cutoff in general.
This verifies mathematics/software, not biological truth.""")),
        tag(nbformat.v4.new_code_cell(
            """sys.path.insert(0, str(PROJECT_ROOT))
from src import formal_revision_audit as r2_audit

example1 = r2_audit.example1_audit()
assert example1["exact_trace_equal"]
assert example1["early_simulated_by_late"]
assert not example1["late_simulated_by_early"]
assert not example1["weak_bisimilar"]
assert example1["direct_witness_check"]["valid"]
assert example1["independent_oracle_agrees"]
display(example1)

r2_hierarchy = [r2_audit.pair_audit(*pair) for pair in r2_audit.hierarchy_pairs()]
assert all(row["independent_oracle_agrees"] for row in r2_hierarchy)
display(pd.DataFrame(r2_hierarchy).drop(columns=["independent"]))
r2_biology = [r2_audit.pair_audit(*pair) for pair in r2_audit.biological_pairs()]
assert all(row["independent_oracle_agrees"] for row in r2_biology)
display(pd.DataFrame(r2_biology)[[
    "case", "left_simulated_by_right", "right_simulated_by_left",
    "weak_bisimilar", "exact_trace_equal", "independent_oracle_agrees"
]])
r2_exhaustive = r2_audit.exhaustive_audit()
assert r2_exhaustive["all_checks_pass"]
display(r2_exhaustive)""")),
    ]
    r3_cells = [
        tag(nbformat.v4.new_markdown_cell("""## R3: fixed-interface death-receptor commitment

The original Calzone model and its documented feedback-deletion variant share
stable-fate predictions under sustained TNF. A selected shared-state continuation
has exact baseline agreement but different withdrawal futures. Global sustained
trace equality is refuted by a verified 12-action word; reverse inclusion is
still undecided. With withdrawal, global traces also differ: this
is not a globally equal-trace/different-branching biological example.

The following cell regenerates the large graphs and all new results. It needs
several GiB of memory, Numba/SciPy and mCRL2; raw AUT export is optional. Earlier
GIM/HPN/formal analyses are retained below as supporting evidence.""")),
        tag(nbformat.v4.new_code_cell("""import subprocess
import json
sys.path.insert(0, str(PROJECT_ROOT))
subprocess.run([sys.executable, 'scripts/fetch_branching_models.py'], cwd=PROJECT_ROOT, check=True)
subprocess.run([sys.executable, 'scripts/run_branching_cases.py'], cwd=PROJECT_ROOT, check=True)
subprocess.run([sys.executable, 'scripts/run_R3_external_audit.py', '--sustained-word-only'], cwd=PROJECT_ROOT, check=True)
r3_baseline = json.loads((PROJECT_ROOT / 'results/death_receptor_sustained_comparison.json').read_text())
r3_external_word = json.loads((PROJECT_ROOT / 'results/death_receptor_sustained_external_word.json').read_text())
assert r3_baseline['trace_analysis']['exact_trace_equal'] is False
assert r3_baseline['weak_simulations']['left_simulated_by_right'] is False
assert r3_baseline['weak_simulations']['right_simulated_by_left'] is None
assert r3_external_word['confirmed']
display(r3_baseline['trace_analysis'])
display(r3_external_word)
r3_summary = json.loads((PROJECT_ROOT / 'results/death_receptor_execution_summary.json').read_text())
r3_witness = json.loads((PROJECT_ROOT / 'results/death_receptor_branching_witness.json').read_text())
display(r3_summary)
display(r3_witness['conditioned_sustained'])
display(r3_witness['history_aggregated_futures'])
display(pd.read_csv(PROJECT_ROOT / 'results/death_receptor_commitment_scan.csv').head(12))
display(json.loads((PROJECT_ROOT / 'results/death_receptor_independent_trace_audit.json').read_text()))
subprocess.run([sys.executable, 'scripts/make_revision_R3_figures.py'], cwd=PROJECT_ROOT, check=True)
from IPython.display import Image
display(Image(filename=str(PROJECT_ROOT / 'revision_R3/R3_Fig1.png')))""")),
        tag(nbformat.v4.new_code_cell("""from dataclasses import replace
from src.death_receptor_analysis import load_variants, OBSERVABLES
from src.controlled_interventions import generate
from src.branching_witness import find_branching_witness, verify_branching_witness
r3_models = load_variants()
shared = tuple(r3_witness['shared_retained_state'].get(v, 0) for v in r3_models[0].variables)
full_continuations = [generate(replace(m, initial=shared), OBSERVABLES, withdraw='TNF') for m in r3_models]
checked = find_branching_witness(full_continuations[0].lts, full_continuations[1].lts)
assert verify_branching_witness(full_continuations[0].lts, full_continuations[1].lts, checked)
assert checked['left_simulated_by_right'] and not checked['right_simulated_by_left']
assert not checked['weak_bisimilar'] and not checked['exact_trace_equal']
display({k:v for k,v in checked.items() if k != 'certificate'})""")),
    ]
    nb.cells[setup_index + 1:setup_index + 1] = r3_cells + gim_cells + benchmark_cells + audit_cells

    summary_index = next(
        i for i, cell in reversed(list(enumerate(nb.cells)))
        if cell.cell_type == "markdown" and cell.source.lstrip().startswith("## Summary")
    )
    nb.cells[summary_index].source = SUMMARY.replace('## Summary',
        '## Summary\n\nR3: endpoint-matched death-receptor variants have different withdrawal futures; '
        'global sustained trace equality is refuted; reverse inclusion remains undecided. '
        'The earlier supporting results follow.', 1).replace(
            'Central GIM result:', 'Secondary GIM result:')
    nb.cells[0].source = """# Locating resolution-dependent behavioral correspondence in qualitative DNA-damage response models
### JBCB R3: death-receptor comparison first; GIM and formal audits retained

R3 separates endpoint agreement, conditioned exact trace equality, and
intervention-dependent futures. Global sustained trace equality is refuted;
the reverse trace inclusion remains undecided. The 12-action counterexample
and mCRL2 checks are reproduced below from the original model rules;
no new experimental validation or uniquely observed hidden state is claimed.

The earlier GIM, HPN and formal audits follow as supporting analyses. All
biological claims are conditional on the encoded models, fixed interface,
initial conditions and update semantics. The feedback/withdrawal phenomenon
was already reported by Calzone et al. (2010); this notebook reconstructs its
relational and reachable-future interpretation.
"""
    nbformat.write(nb, NOTEBOOK)


if __name__ == "__main__":
    main()
