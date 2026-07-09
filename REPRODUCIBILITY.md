# Reproducibility guide (for reviewers and readers)

This repository contains everything needed to **replicate every quantitative
result, table and figure** in the article

> *A concurrency-theoretic method for behavioural comparison of conserved
> molecular modules across species: an Arabidopsis–animal cancer case study*
> (submitted to Elsevier **BioSystems**).

The manuscript itself is **not** included here (only the material needed to
reproduce its results). Everything below runs offline: there is **no network
access, no external database and no downloaded data**. All inputs are the
literature-curated models hard-coded in [`src/concurrent_biomodels.py`](src/concurrent_biomodels.py),
and all randomness uses **fixed seeds**, so the outputs are deterministic.

Typical end-to-end runtime: **well under a minute** on a laptop.

---

## 1. Prerequisites

* **Python ≥ 3.10**
* **System Graphviz** (the `dot` binary), used to draw the Petri-net and LTS
  diagrams:
  * macOS: `brew install graphviz`
  * Debian/Ubuntu: `sudo apt-get install graphviz`
  * conda: included in `environment.yml`

The **formal core** (`src/concurrent_biomodels.py`) depends only on the Python
standard library. `numpy`, `pandas`, `matplotlib`, `networkx` and `pydot` are
required only to render figures and write the CSV/LaTeX tables.

Tested with: Python 3.11, numpy 1.26, pandas 2.x/3.x, matplotlib 3.10,
networkx 3.3, pydot 4.0, Graphviz 12.

---

## 2. Set up the environment

Using pip (virtual environment recommended):

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
python -m pip install -r requirements.txt
```

or using conda:

```bash
conda env create -f environment.yml
conda activate bisimulationmol
```

---

## 3. Reproduce everything with one command

```bash
make figures      # regenerates every file under figs/ and results/
```

or, without `make`:

```bash
python make_figures.py
```

To also confirm **bit-for-bit determinism** of the tracked tables (this is what
CI runs on every push):

```bash
make verify       # regenerates results/ and fails if anything changed
```

To print just the per-module verdicts and diagnostics to the terminal:

```bash
make analysis     # == python src/concurrent_biomodels.py
```

To execute the exploratory notebook end to end:

```bash
make notebook
```

---

## 4. What each output corresponds to in the paper

`make figures` writes PNG figures to `figs/` (regenerated, not tracked) and
CSV/LaTeX tables to `results/` (tracked, so they can be diffed).

### Figures (`figs/`)

| Output file | Paper figure |
|---|---|
| `fig_pipeline.png` | The six-phase method (pipeline) |
| `fig_phase1_hallmarks.png` | Genes per cancer hallmark (H. sapiens vs A. thaliana) |
| `fig_phase2_conservation.png` | Conservation index per module |
| `fig_ddr_petri_animal.png`, `fig_ddr_petri_plant.png` | GIM (DNA-damage) Petri nets |
| `fig_ddr_lts_animal.png`, `fig_ddr_lts_plant.png` | GIM reachability graphs (LTS) |
| `fig_rcd_petri_animal.png`, `fig_rcd_petri_plant.png` | RCD (cell-death) Petri nets |
| `fig_phase6_spectrum.png` | Partial-comparability spectrum |
| `fig_phase6_properties.png` | Behavioural-property matrix |
| `fig_robustness.png` | Verdict invariance under τ-refinement |
| `fig_nullbaseline.png` | Label-permutation null baseline |
| `fig_kconvergence.png` | Behavioural distance vs truncation depth k |
| `fig_generalization.png` | Cross-organism generalisation (cell cycle) |

### Tables and data (`results/`)

| Output file | Paper element |
|---|---|
| `phase6_table.tex` | Behavioural properties + verdict per module (main results table) |
| `gim_provenance.tex` | Model-construction provenance for the GIM module |
| `model_provenance_all.tex` | Appendix A: transition-level provenance (all modules) |
| `generalization.tex` / `generalization.csv` | Cross-organism generalisation table |
| `phase1_hallmarks.csv` | Gene counts per hallmark |
| `phase2_conservation.csv` | Conservation index per module |
| `phase6_comparisons.csv` | Per-module bisimulation / simulation / distance |
| `robustness.csv` | τ-refinement invariance (300 refinements/module) |
| `nullbaseline.csv` | Label-permutation p- and BH q-values |
| `interface_necessity.csv` | Single-label interface-necessity test |
| `null_seed_sensitivity.csv` | Null-test q-value ranges across 5 seeds |
| `kconvergence.csv` | Distance dₖ as a function of k |

---

## 5. How the verdicts are computed (auditability)

Verdicts are produced by a **general algorithm** over auditable models, not
hard-coded. The key entry points in `src/concurrent_biomodels.py` are:

* `run_full_analysis()` — per-module strong/weak bisimulation, simulation
  preorders and behavioural distance;
* `robustness_under_tau_refinement()` — invariance under silent refinements;
* `null_baseline_suite()` — label-permutation null test with Benjamini–Hochberg
  correction;
* `generalization_analysis()` — the same routine across mouse/yeast/Arabidopsis
  vs a human reference, plus a scrambled control;
* `MODEL_PROVENANCE` / `provenance_coverage()` — every Petri-net transition is
  traced to a literature statement, and coverage is audited automatically.

---

## 6. Troubleshooting

* **`pydot`/Graphviz error, or empty Petri-net images** — ensure the system
  `dot` binary is installed and on `PATH` (`dot -V`). `pip install pydot` alone
  is not enough; Graphviz is a separate system package.
* **`make verify` reports a difference** — this should not happen. If it does,
  check your Python/library versions against Section 1 and open an issue.
