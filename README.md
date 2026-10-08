# Journal: Experiments for the Accepted JBCB Article

[![Reproducibility](https://github.com/cero1979/BisimulationMol/actions/workflows/reproduce.yml/badge.svg)](https://github.com/cero1979/BisimulationMol/actions/workflows/reproduce.yml)

**Journal of Bioinformatics and Computational Biology (World Scientific)**

> **Locating resolution-dependent behavioral correspondence in qualitative DNA-damage response models**
>
> Carlos Ramirez Ovalle. Accepted October 2, 2026. Manuscript JBCB-1505.

This is the **Journal experiment repository** for the accepted article. It
contains only that article, its supplementary validation, and the code, public
inputs, outputs and tests needed to reproduce its experiments. Publication DOI,
volume and page details will be added when available.

## Read the Article

- [Article PDF](Journal/main.pdf) and [LaTeX source](Journal/main.tex).
- [Supplementary validation PDF](Journal/supplement.pdf) and [source](Journal/supplement.tex).
- [Journal source package](Journal/Journal.zip): flat ZIP with both sources,
  compiled PDFs, all six figures and the World Scientific class.
- [Experiment notebook](notebooks/metodologia_multiescala.ipynb).
- [Reproducibility instructions](REPRODUCIBILITY.md).

The bibliographies are embedded in the two LaTeX documents. No external `.bib`
file, older manuscript or revision assembler is required. The supplementary
validation is part of the accepted scientific evidence, not an obsolete draft.

## What the Experiments Establish

| Experiment | Result | Scope |
|---|---|---|
| Calzone death-receptor variants under sustained TNF | Both reach survival, apoptosis and necrosis; global trace equality is refuted by a verified 12-action word | Endpoint agreement is not equality of all trajectories; reverse trace inclusion remains undecided |
| Withdrawal from a shared reachable state | Sustained continuations have exactly equal languages; withdrawal gives one-way simulation and different CASP3 futures | State-conditioned, fixed-interface model comparison, not recovery of an apoptotic cell |
| Global withdrawal comparison | Exact counterexamples refute both trace inclusions and both weak-simulation directions | Not a globally equal-trace/different-branching biological example |
| GIM observational interfaces | A/B are weakly bisimilar; C has neither simulation direction; PN-GDDA stays 0.9976 | Correspondence boundary within three declared interfaces, not a unique biological resolution |
| Formal and software checks | Six constructed classes recovered; independent directional and exhaustive 67,600-pair audits agree | Correctness evidence on declared finite systems, not experimental biological validation |
| Structural comparator | Direct 151-graphlet/592-slot PN-GDDA and an independent Holmes reference check | Structural similarity does not determine labeled reachable behavior |
| HPN-DREAM/CASPOTS | Nine cross-model comparisons, held-out response scores and semantic sensitivity | Exploratory; native-cell specificity is not established (`p=0.25`) |

The feedback/withdrawal phenomenon was described by Calzone et al. (2010).
The analysis reconstructs its behavioral interpretation; it does not claim a
new wet-lab discovery. The curated GIM and other module pairs, formal controls,
and held-out data analyses are retained because the article or supplement uses
them. Unsupported conservation rankings and unrelated generalization examples
are not part of this repository.

## Quick Start

Use Python 3.11 and install the dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
make public-models hpn-data test
```

Public inputs are included and SHA-256 checked. Downloads occur only when an
input is absent. Install Graphviz (`dot`) for drawings and **mCRL2 202607.0**
(`ltscompare`) for external checks. Set `MCRL2_LTSCOMPARE` if needed. Without
mCRL2, two external-oracle tests are explicitly skipped; that is not a complete
external validation.

| Task | Command | Requirements |
|---|---|---|
| Inspect results | Open the notebook, PDFs and `results/` | No execution |
| Test implementation and inputs | `make public-models hpn-data test` | Python; mCRL2 for external tests |
| Reproduce the main biological case | `make death-receptor` | Python, mCRL2, several GiB of free RAM |
| Regenerate and check scientific outputs | `make verify` | Python, Graphviz, mCRL2; tested on an 18 GiB host |
| Execute the notebook | `make notebook` | Same scientific environment |
| Compile article, supplement and flat ZIP | `make package` | pdfLaTeX; no experiment rerun |
| Repeat independent held-out scores | `make caspots-validation` | Separate `environment-hpn.yml` environment |

`make verify` checks scientific decisions, counterexamples, model sizes/hashes,
prefix counts and execution limits. It excludes only scalability timings and
two declared bounded-search progress counters that depend on machine speed.
The [guide](REPRODUCIBILITY.md) specifies the exact comparison contract.

## Repository Layout

| Path | Role |
|---|---|
| `Journal/` | Accepted article, supplementary validation, six figures, class and flat ZIP |
| `src/` | Model import, execution, formal comparison and independent oracles |
| `scripts/` | Hash-checked inputs, experiments, external audits and document build |
| `data/` | Original public models and HPN-DREAM/CASPOTS inputs |
| `results/` | Experiment outputs, certificates, provenance and resource protocols |
| `notebooks/` | Integrated experiment notebook |
| `tests/` | Scientific regression and Journal artifact checks |

The preregistration and dated resource amendments in `results/branching_case_*`
are retained as experiment provenance. They are not alternative article
versions. Generated working files in `figs/` and `tmp/` are not distributed.

## Citation and Licenses

Use [CITATION.cff](CITATION.cff) to cite the article and repository, and record
the Git commit used for a reproducibility run. GitHub's source archive is the
code/data snapshot; `Journal/Journal.zip` is the LaTeX package, not a substitute
for the experiment repository.

Original code is provided under [MIT](LICENSE). Third-party models and datasets
retain their original attribution and licensing; their source URLs, pinned
commits and SHA-256 checksums are documented in the input registries.
