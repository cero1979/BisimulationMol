# Observational comparison of qualitative biological network models

[![Reproducibility](https://github.com/cero1979/BisimulationMol/actions/workflows/reproduce.yml/badge.svg)](https://github.com/cero1979/BisimulationMol/actions/workflows/reproduce.yml)

This repository is the end-to-end reproducibility package for the manuscript:

> *Observational comparison of qualitative biological network models: a
> reproducible Petri-net framework*

The manuscript is prepared for **Network Modeling Analysis in Health
Informatics and Bioinformatics (NetMAHIB)**. Its contribution is computational:
it tests whether two explicit qualitative models have the same observable
behaviour under a declared interface. It does **not** infer experimental or
organism-level biological equivalence from graph structure.

## Reproduction levels

The repository supports three progressively heavier audits. Public input files
are committed for offline use; the fetch targets verify their SHA-256 digests
and contact the source repositories only when a file is absent or invalid.

| Level | Purpose | Command | Additional requirements |
|---|---|---|---|
| Inspect | Read the executed analysis and committed outputs | Open `notebooks/metodologia_multiescala.ipynb` and `results/` | None |
| Core | Re-run formal tests, figures and deterministic tables | `make public-models hpn-data verify` | Python, Graphviz, mCRL2 |
| Full | Recompute CASPOTS scores, notebook, manuscript and upload ZIPs | `make caspots-validation notebook manuscript package` | Core tools, Conda, LaTeX |

`make verify` is the primary reproducibility check. It runs 16 tests,
regenerates the scientific outputs and fails if any deterministic tracked
result differs. Runtime measurements are reported but excluded from byte-level
comparison because they depend on hardware.

## What changed after editorial review

The revised study addresses five indispensable objections:

1. **Computational-method framing.** The title, abstract, research question and
   conclusions now concern model comparison rather than cross-species
   biological equivalence.
2. **Claim discipline.** Every result is stated as a relation between curated
   models conditional on their encoded transitions and observational interface.
3. **Independent validation.** Six synthetic pairs have construction-level
   ground truth; all strong and weak decisions are cross-checked with mCRL2,
   and the full path is exercised on two public GINsim models.
4. **Scalability and case-study role.** Runtime and candidate-relation growth are
   measured up to 129 x 145 states. The Arabidopsis-animal comparison is an
   illustration of the workflow, not biological validation of the species.
5. **Held-out biological data.** Structure-only representatives of three public
   HPN-DREAM Boolean-network families are fixed without test-value access,
   cross-checked with mCRL2 and scored on reserved mTOR-inhibitor responses.
   The negative specificity result is retained rather than converted into a
   biological-equivalence claim.

## Main results

| Validation layer | Result | Supported interpretation |
|---|---|---|
| Six construction-ground-truth pairs | 6/6 formal classes recovered | The implementation distinguishes equivalence, directional simulation and non-comparability |
| Independent mCRL2 oracle | 24/24 synthetic/public strong and weak decisions agree | The principal formal decisions are not specific to the Python implementation |
| HPN-DREAM cross-cell comparisons | 18/18 Python/mCRL2 decisions agree | The data-conditioned transition systems are reproducibly classified |
| Held-out native-cell ranking | Native model first or tied in 2/3 cells; exact `p=0.25` | Compatibility is reproduced; cell specificity is not established |
| Formal class versus experimental distance | Spearman `rho=0.091`; exact `p=0.111` | No empirical concordance is established in this sample |

Machine-readable evidence is in
[`results/synthetic_benchmark.csv`](results/synthetic_benchmark.csv),
[`results/mcrl2_synthetic_validation.csv`](results/mcrl2_synthetic_validation.csv),
[`results/hpn_dream_formal_data_validation.csv`](results/hpn_dream_formal_data_validation.csv)
and [`results/hpn_dream_caspots_summary.json`](results/hpn_dream_caspots_summary.json).

The synthetic suite recovers all six predeclared formal classes: strong
equivalence, weak equivalence, two directions of one-way simulation, and two
non-comparable cases. On the binary weak-equivalence task:

| Method | Accuracy | False positives | False negatives |
|---|---:|---:|---:|
| Weak bisimulation | 1.000 | 0 | 0 |
| Trace equality at depth 8 | 0.833 | 1 | 0 |
| Structural profile at threshold 0.9 | 0.500 | 2 | 1 |

The Python implementation and mCRL2 202607.0 agree on all 24 strong/weak
decisions across six synthetic and six public-model controls. Exact mCRL2
weak-trace outcomes match all 12 predeclared trace controls. The public Boolean
mammalian cell-cycle model yields 826 reachable states and 3,413 edges; the
multilevel p53-Mdm2 model yields 17 states and 26 edges. Source files are stored
with their original URLs and SHA-256 digests.

The data-backed analysis adds 284 public CASPOTS networks for BT20, BT549 and
MCF7. Across three shared held-out perturbations, Python and mCRL2 agree on all
18 strong/weak decisions: six cross-cell pairs have one-way simulation and
three are not comparable. CASPOTS compatibility RMSE is reproduced twice
identically, but native medoids rank first or tie in only two of three cell
lines. Neither native specificity (exact p=0.25) nor formal-class/data
concordance (p=0.111) is established. This is an informative negative
validation boundary, not evidence of prognostic performance.

### Data separation and provenance

- Public GINsim and HPN-DREAM/CASPOTS artifacts are tied to source URLs,
  historical commits and SHA-256 digests.
- The BT20, BT549 and MCF7 representatives are selected as structure-only
  family medoids before held-out response values are opened; an automated test
  enforces this anti-leakage boundary.
- Experimental RMSE uses only common post-zero held-out measurements. Time zero
  initializes the transition systems and is not reused as an outcome.
- The retrospective family oracle is labeled separately because it does inspect
  the held-out responses and is not a blind performance estimate.

The reference scalability run reached 129 x 145 state pairs and approximately
0.54 s on an Apple M3 Pro. Timings are machine-dependent; model sizes,
relations and classifications are deterministic.

In the illustrative curated case, GIM, DCE and SPS are weakly bisimilar, RCD
has one-way simulation, and AID is not comparable. These outputs describe the
encoded models at the selected interface resolution only.

## Repository layout

```text
src/concurrent_biomodels.py       Formal engine and curated case-study models
src/method_benchmark.py           Synthetic validation, baselines and scaling
src/public_validation.py          SBML/GINML import, AUT export and mCRL2 oracle
src/hpn_dream_validation.py       Blind public-model/data comparison and exact test
data/public_models/               Hash-verified public GINsim model files
data/hpn_dream/                    Hash-verified HPN-DREAM/CASPOTS families and data
tests/test_method_benchmark.py    Regression and construction-ground-truth tests
tests/test_external_validation.py Public-model and independent-oracle tests
tests/test_hpn_dream_validation.py Data integrity, anti-leakage and mCRL2 tests
notebooks/metodologia_multiescala.ipynb
                                  Executed end-to-end analysis notebook
make_figures.py                   Regenerates figures and machine-readable results
results/                          CSV and LaTeX result tables
figs/                             Regenerated figures (git-ignored)
paper/netmahib/main.tex           NetMAHIB manuscript in Springer Nature format
paper/netmahib/references.bib     Manuscript bibliography
scripts/build_netmahib_package.py Builds a flat Editorial Manager ZIP
REPRODUCIBILITY.md                Reviewer-oriented reproduction guide
```

## Quick start

Python 3.10 or newer, system Graphviz and mCRL2 202607.0 are required for the
complete validation. The formal engine and model importers use only the Python
standard library.

```bash
python -m pip install -r requirements.txt
make public-models
make hpn-data
make verify
```

For individual stages, use `make external-validation`, `make hpn-validation`,
`make test`, `make figures` or `make notebook`. Expected numeric results,
artifact-to-figure mappings and troubleshooting are documented in
[`REPRODUCIBILITY.md`](REPRODUCIBILITY.md).

The CASPOTS RMSE audit has additional pinned dependencies:

~~~bash
conda env create -f environment-hpn.yml
make caspots-validation
~~~

To compile the manuscript and build the source-only submission archive:

```bash
make manuscript
make package
```

The manuscript archive is `submission/netmahib_latex_flat.zip`. It contains a
flat, self-contained LaTeX source set: `main.tex`, the Springer class and
bibliography style, `references.bib`, `main.bbl`, and 12 vector artwork files
that compose the eight figures used by the manuscript. A second archive,
`submission/netmahib_reproducibility.zip`, contains the code, public models,
tests, result tables, workflow and executed notebook for upload as supplementary
material. Author and affiliation information are already inside `main.tex`; a
separate title-page upload is not required to compile the source.

## Reproducibility contract

```bash
make verify
```

This regenerates all tracked scientific tables and fails if deterministic
outputs differ. `results/scalability_runtime.csv` is deliberately excluded from
bit-for-bit comparison because elapsed time depends on hardware and system
load. Its structural companion, `results/scalability_structure.csv`, remains
deterministic and is checked.

The public repository is <https://github.com/cero1979/BisimulationMol>.
See [REPRODUCIBILITY.md](REPRODUCIBILITY.md) for commands, expected outputs and
the mapping between repository artifacts and manuscript figures/tables.

## License and citation

Code is released under the [MIT License](LICENSE). Citation metadata are in
[CITATION.cff](CITATION.cff).
