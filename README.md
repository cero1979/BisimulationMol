# Behavioural comparability of conserved molecular modules across species

A **reproducible** implementation of a multiscale method that couples
**conserved active subnetworks** (biological-computational level) with
**concurrent formalisation as Petri nets** and **behavioural equivalences**
(formal level), to compare conserved molecular modules across biological
systems. The principal case study asks whether *A. thaliana* can serve as a
**partial model** of molecular sub-mechanisms associated with specific cancer
hallmarks.

> **This repository is the reproducibility package** for the article submitted
> to Elsevier *BioSystems*. It contains only what is needed to **replicate the
> results** reported in the paper; the manuscript itself is intentionally **not**
> included. Start with [`REPRODUCIBILITY.md`](REPRODUCIBILITY.md) for a
> step-by-step, reviewer-oriented guide. Canonical location:
> <https://github.com/cero1979/BisimulationMol>.

The method is grounded in:

- **Clavijo-Buriticá, Sosa, …, Quimbaya.** *Use of Arabidopsis thaliana as a model
  to understand specific carcinogenic events.* **Heliyon** 9 (2023) e15367.
  <https://doi.org/10.1016/j.heliyon.2023.e15367> — prioritises five conserved
  hallmarks (DCE, ERI, RCD, SPS, GIM).
- **Quimbaya, Vandepoele, Raspé *et al.*** *Identification of putative cancer genes
  through data integration and comparative genomics between plants and humans.*
  **Cell. Mol. Life Sci.** 69 (2012) 2041–2055.
  <https://doi.org/10.1007/s00018-011-0909-x>.

## Layout

```
├── src/concurrent_biomodels.py       # Engine: Petri nets, LTS, weak/strong
│                                      #  bisimulation, simulation, distance,
│                                      #  robustness & null-baseline diagnostics,
│                                      #  and curated per-module models
├── notebooks/
│   └── metodologia_multiescala.ipynb  # Notebook: run/validate/compare (6 phases
│                                      #  + robustness + significance + k-sweep)
├── make_figures.py                   # Regenerates figs/ and results/
├── results/                          # Reference tables/CSV (+ *.tex) used by the paper
├── figs/                             # Generated figures (PNG; regenerated, git-ignored)
├── requirements.txt                  # Python dependencies (pip)
├── environment.yml                   # Python dependencies (conda)
├── Makefile                          # make setup | analysis | figures | verify | notebook
├── REPRODUCIBILITY.md                # Step-by-step guide for reviewers
├── CITATION.cff                      # How to cite this work
├── LICENSE                           # MIT licence
└── .github/workflows/reproduce.yml   # CI: regenerate + verify on every push
```

## Requirements

- Python ≥ 3.10 with `numpy`, `pandas`, `matplotlib`, `networkx`, `pydot`
  (see `requirements.txt`). The **formal core** (`src/`) uses only the standard
  library, so the numerical verdicts do not depend on third-party versions.
- System **Graphviz** (the `dot` binary) for the Petri-net / LTS drawings
  (macOS: `brew install graphviz`; Debian/Ubuntu: `apt install graphviz`).

Tested with Python 3.11, numpy 1.26, pandas 2.x/3.x, matplotlib 3.10,
networkx 3.3, pydot 4.0 and Graphviz 12.

```bash
pip install -r requirements.txt
```

## Usage

```bash
python src/concurrent_biomodels.py       # print the per-module verdict + diagnostics
python make_figures.py                   # regenerate everything under figs/ and results/
make verify                              # regenerate results/ and check determinism
jupyter lab notebooks/metodologia_multiescala.ipynb   # interactive exploration
```

The article is submitted separately to *BioSystems* and is not part of this
repository. See [`REPRODUCIBILITY.md`](REPRODUCIBILITY.md) for the full,
reviewer-oriented walkthrough and a table mapping each output file to the
corresponding figure or table in the paper.

## Method in one paragraph

For each hallmark module we curate a conserved subnetwork (Phase 2), fix a common
**observational interface** of experimentally meaningful read-outs (Phase 3),
encode a plant and an animal Petri net whose every transition is traced to a
literature statement (Phase 4), and decide partial comparability from the
reachability graphs using **weak bisimulation**, **simulation preorders** and a
**trace-based behavioural distance** (Phases 5–6). Safeguards guard against
confirmation bias: verdicts must be **invariant under silent (τ) refinement**, a
**label-permutation null test** quantifies how unlikely the observed
comparability is under a scrambled interface with BH-FDR correction, and a
`k`-sweep verifies trace-depth stability. Additional adversarial checks test
single-label interface necessity and null-test seed sensitivity.

## Result (per-module verdict)

| Module | Sub-mechanism | Strong bisim. | Weak bisim. | Plant⊑Animal | Animal⊑Plant | d | Null p/q | Verdict |
|---|---|:-:|:-:|:-:|:-:|:-:|:-:|---|
| GIM | DNA repair | – | ✓ | ✓ | ✓ | 0.00 | 0.006/0.030 | Comparable (weak bisim.) |
| DCE | Energy metabolism | – | ✓ | ✓ | ✓ | 0.00 | 0.022/0.037 | Comparable (weak bisim.) |
| SPS | Cell cycle | – | ✓ | ✓ | ✓ | 0.00 | 0.013/0.034 | Comparable (weak bisim.) |
| RCD | Cell death/autophagy | – | – | ✓ | – | 0.14 | 0.032/0.040 | Partial; seed-borderline |
| AID | Immune (control) | – | – | – | – | 0.43 | 0.154/0.154 | Not comparable |

**Reading.** GIM/DCE/SPS are **weakly** bisimilar but **not strongly** so: the
species-specific internal events (SMR induction, restriction-point tuning, redox
buffering) differ, and it is the weak abstraction of τ that exposes the functional
equivalence — a formal statement of why the right cross-species comparison is
*observational*, not strictly structural. RCD is comparable only by simulation
(the plant reproduces autophagy and death commitment but not canonical caspase
apoptosis). Its null-test support is borderline under seed re-sampling, so it is
kept as a partial claim rather than promoted to equivalence. AID is a **negative
control**: not comparable, and — unlike the conserved modules — *not*
significantly closer than a scrambled interface (q = 0.154), which shows the
method discriminates rather than rubber-stamps.

Verdicts are computed by a **general algorithm** over auditable, literature-traced
models (see `MODEL_PROVENANCE` in the engine); they are not hard-coded. All
numbers above regenerate deterministically (fixed seeds) via `make_figures.py`.

## Generalisation (not tied to Arabidopsis)

The formal comparison API compares any two module models over a shared interface;
the Arabidopsis-specific functions are just one curated case-study registry.
`generalization_analysis()` applies the *same* routine to one conserved module
(the cell cycle) across a panel of model organisms against a human reference,
plus a scrambled same-alphabet control:

| Organism (vs Human) | Strong bisim. | Weak bisim. | d | Verdict |
|---|:-:|:-:|:-:|---|
| Mouse | ✓ | ✓ | 0.00 | strong (near-identical mammalian circuit) |
| Yeast | – | ✓ | 0.00 | weak bisimulation |
| Arabidopsis | – | ✓ | 0.00 | weak bisimulation |
| Scrambled-control | – | – | 0.92 | not comparable |

Verdict *strength* behaves sensibly in this small panel (mouse strong;
yeast/Arabidopsis weak), while the scrambled control shows that shared labels
alone are not enough.
The method thus reads as a **general method for comparing conserved molecular
modules across biological systems**, with the plant–animal cancer study as its
principal case. It generalises across *modules* and *systems*, but **not** to
whole organisms or arbitrary isolated molecules unless they can be represented as
module-level transition systems.

## Reproducibility

Every figure and table in the paper regenerates **deterministically** (fixed
random seeds) from the curated models, with no network access or external data.
The recommended entry point is:

```bash
make figures     # regenerate figs/ and results/
make verify      # regenerate results/ and fail if anything changed (determinism)
```

A GitHub Actions workflow ([`.github/workflows/reproduce.yml`](.github/workflows/reproduce.yml))
re-runs this on every push and checks that the tracked `results/` are reproduced
bit-for-bit. Full details, prerequisites and an output–to–paper mapping are in
[`REPRODUCIBILITY.md`](REPRODUCIBILITY.md).

## Citing this work

If you use this software or method, please cite the article (Elsevier
*BioSystems*, under review) and this repository. Machine-readable metadata is in
[`CITATION.cff`](CITATION.cff); GitHub renders a “Cite this repository” button
from it.

## License

Released under the [MIT License](LICENSE).
