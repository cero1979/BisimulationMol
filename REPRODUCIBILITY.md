# Journal Reproducibility Guide

This repository reproduces the accepted **Journal of Bioinformatics and
Computational Biology** article, *Locating resolution-dependent behavioral
correspondence in qualitative DNA-damage response models*.

The canonical sources are `Journal/main.tex` and `Journal/supplement.tex`.
They are standalone documents with embedded bibliographies and the official
World Scientific class. No earlier manuscript, reviewer response or assembly
baseline is required. Pin the repository's Git commit for an exact code/data
snapshot. The flat `Journal/Journal.zip` is for LaTeX production, not experiments.

## 1. Environment and Public Inputs

Use Python 3.11, the dependencies in `requirements.txt`, Graphviz (`dot`), and
**mCRL2 202607.0** (`ltscompare`). pdfLaTeX is needed only for document builds.

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
make public-models hpn-data
```

Alternatively, `conda env create -f environment.yml` installs the scientific
Python environment and Graphviz. Install mCRL2 separately and set
`MCRL2_LTSCOMPARE=/path/to/ltscompare` when it is not on `PATH`. The CI workflow
pins the official Debian asset by SHA-256
`00cb4c347638b3a418fb67c9d67b8d2bf2245e10d4affa4cd993b1c357bde969`.

Original public inputs are committed for offline use. The fetch commands
verify hashes and download only absent inputs; a wrong hash is rejected.

| Input | Registry and provenance |
|---|---|
| Original Calzone 2010 death-receptor model | `src/death_receptor_analysis.py`, `scripts/fetch_branching_models.py` |
| Mammalian cell-cycle and p53-Mdm2 controls | `src/public_validation.py`, `scripts/fetch_public_models.py` |
| HPN-DREAM/CASPOTS families, learning sets and held-out responses | `scripts/fetch_hpn_dream.py`, pinned public commit `95e3c74` |
| Five curated plant/animal module pairs and GIM interfaces | `src/concurrent_biomodels.py`, including transition-level literature provenance |

No credentials or confidential data are needed. Third-party inputs retain their
original attribution and licensing; MIT applies to the original repository code.

## 2. Main Death-Receptor Experiment

```bash
make death-receptor
make death-receptor-word
```

The first command regenerates the large execution graphs, terminal futures,
simulation witnesses, exact trace counterexamples and event-depth scan. The
second independently checks the sustained 12-action word with mCRL2.

The fixed configuration and dated resource amendments are retained in
`results/branching_case_*`. These files establish the analysis protocol, not
alternative manuscript versions. No rule or observational interface was retuned
after relation results. Only the hidden sink readouts NonACD, Apoptosis and
Survival are omitted in the large graphs; Supplement S5 states the reduction
argument and the direct original-model continuation checks.

Numba compiles truth tables obtained from the GINML importer; NumPy/SciPy provide
compact graph storage and strongly connected components. Four graphs contain
about 6.9 million states altogether. Reserve several GiB of free RAM; the
reference host has 18 GiB. Optional AUT export needs additional disk space:

```bash
python scripts/run_branching_cases.py --export-aut
python scripts/run_death_receptor_external_audit.py
```

The full-graph audit reads the four files under `tmp/Journal/` and bounds each
mCRL2 call at 180 seconds. Timeouts are inconclusive, not negative verdicts.
Strong relations on the hidden-sink quotient are quotient-specific; the
reduction automatically preserves weak properties only.

Sustained subset discovery is bounded at 100,000 pairs, 2 GB stored subsets and
600 seconds; withdrawal at 10,000 pairs, 250 MB and 180 seconds. The driver
separately rechecks the known sustained counterexample by exact closure
propagation. Refutation of equality therefore does not depend on completing
discovery. `make death-receptor-word` regenerates both sustained graphs and
uses mCRL2 antichain inclusion of the word's finite prefix language, without
pickle caches or pre-existing AUT files.

The outputs distinguish three different claims:

- **Global sustained comparison:** exact trace equality is false; the reverse
  inclusion remains undecided. A verified 12-action word suffices to refute
  equality even when discovery reaches a resource cap.
- **Selected shared-state continuation:** sustained languages are exactly
  equal; withdrawal yields one-way simulation and different CASP3 futures.
- **Global withdrawal comparison:** two exact words refute both trace
  inclusions and weak-simulation directions.

The witness distinguishes one shared retained state from the 78 hidden states
compatible with its visible history and from their aggregate futures. Scan rows
count states after exactly 0-40 raw updates, not probabilities or minutes;
post-withdrawal futures are exhaustive, not truncated at 40.

| Output in `results/` | Role |
|---|---|
| `death_receptor_execution_summary.json` | Graph sizes, hashes and terminal fates |
| `death_receptor_sustained_comparison.json` | Global baseline result and its limitations |
| `death_receptor_withdrawal_comparison.json` | Global intervention comparison |
| `death_receptor_branching_witness.json` | Shared history/state, local certificate and aggregated futures |
| `death_receptor_trace_equivalence.json` | Exact/capped trace checks with completion status |
| `death_receptor_commitment_scan.csv` | Event-depth scan |
| `death_receptor_independent_trace_audit.json` | Original 28-node rule/product checks of withdrawal counterexamples |
| `death_receptor_sustained_sparse_audit.json` | Independent sparse audit and 53-update accepting path |
| `death_receptor_sustained_external_word.json` | Independent mCRL2 sustained-word check |
| `death_receptor_sustained_discovery.json` | Retained discovery provenance |

The regression tests verify the accepting path against the original 28-node
rules. The bounded direct full-model product search for the longer sustained
word was inconclusive and is not counted as successful evidence.

## 3. Supporting Experiments and Independent Checks

```bash
make gim-interface
make pn-gdda
make external-validation
make formal-audit
make hpn-validation
make test
```

- GIM changes only the observational interface. The three sensitivity rows
  retain PN-GDDA 0.9976, weak bisimulation at A/B and neither simulation at C.
- PN-GDDA generates the 151-topology/592-slot catalog, the 576-orbit sensitivity
  audit, native module scores and construction-level comparator controls.
- External validation tests six synthetic and six public-model controls with
  mCRL2, and runs the independent exhaustive simulation oracle.
- `src/formal_audit.py` constructs weak targets directly from raw edges. Its
  outputs include Example 1, three hierarchy witnesses, 32 directional pair
  records and the expanded 67,600-pair exhaustive audit. The external hierarchy
  script checks simulation preorders only when the inputs are tau-free.
- HPN uses structure-only medoid selection without held-out test access.
  Nine asynchronous pair/condition comparisons retain all directions; global
  synchronous updating preserves seven classes. Continuous diagnostics retain
  all 216 condition-stratified permutations. No ordinal formal-class statistic
  or supported cell-specific predictive advantage is claimed.

Without `ltscompare`, two unit tests explicitly skip the external oracle. The
full validation commands require the tool and must not be described as complete
when those tests are skipped.

To execute the Holmes reference implementation, with a JDK and network access:

```bash
make holmes-pn-gdda
```

The script downloads Holmes 1.1.1, checks JAR SHA-256
`1747a9798c074a4e8a560cded9396ec3d0be05af2d948953c7730d5e623f044c`,
checks the 151 topology signatures/592 assignments and compares the reference
score. No Holmes binary is redistributed.

To recompute the twelve held-out CASPOTS scores twice:

```bash
conda env create -f environment-hpn.yml
make caspots-validation
```

This separate environment pins Python 3.11, CASPO 4.0.3, Clingo 5.8.0, NuSMV
2.6.0 and CASPOTS commit `cee54b8`. Original input bytes are retained; the MCF7
inhibitor-header normalization occurs only in temporary CASPOTS inputs. Included
scores can be inspected without installing this optional solver environment.

## 4. Figures, Notebook and Regression Contract

```bash
make figures
make notebook
make verify
```

`make figures` regenerates supporting results/diagnostics and all six Journal
figures. It uses the committed death-receptor outputs; rerun `make death-receptor`
first when those outputs need regeneration.

| Figure | Content | Generator |
|---|---|---|
| `Journal/Fig1.pdf` | Death-receptor comparison | `scripts/make_death_receptor_figure.py` |
| `Journal/Fig2.pdf` | GIM interfaces and outcomes | `scripts/make_gim_figure.py` |
| `Journal/Fig3.pdf`, `Journal/Fig4.pdf` | Detailed GIM Petri nets | `make_figures.py` |
| `Journal/SFig1.pdf` | Construction-level comparator benchmark | `make_figures.py` |
| `Journal/SFig2.pdf` | Exploratory HPN-DREAM results | `make_figures.py` |

The notebook is canonical and executes directly, without a historical cell
assembler. It includes the principal biological analysis, GIM, formal controls,
PN-GDDA, HPN, curated-pair diagnostics and measured scaling. Machine-dependent
timings are not expected to equal the reference timings.

`make verify` regenerates the regular experiment outputs and compares all
tracked result files with HEAD using `scripts/verify_result_reproducibility.py`.
The optional Holmes/CASPOTS/full-graph commands above reproduce the additional
external-tool evidence; retained discovery/protocol records are provenance.
The comparison excludes `results/scalability_runtime.csv` and only
`subset_product_states` / `stored_subset_bytes` at the declared trace-analysis
paths in the five sustained/withdrawal comparison/trace JSON files. Every other
JSON field stays strict, including limits, completion status, verdicts,
counterexamples, prefix counts and model sizes/hashes. Other result files are
compared byte-for-byte. A timeout is never turned into an equivalence decision.

## 5. Compile the Article and Supplement

```bash
make package
```

The builder copies only the nine canonical source/class/figure files into an
empty directory and runs pdfLaTeX three times per document. It rejects unresolved
references, missing artwork, layout warnings and external bibliography inputs.
It writes `Journal/main.pdf`, `Journal/supplement.pdf` and a flat eleven-file
`Journal/Journal.zip`, then extracts the ZIP and independently rebuilds both PDFs
without packaged PDFs or cached auxiliary files. `Journal/build_validation.json`
records file hashes and build checks.

The accepted scientific text is not reassembled or numerically rewritten by
the build. Regression tests preserve all 19 accepted mathematical environments
and check the current interpretation, references, figures and formal outputs.
Renamed paths and the data-availability wording identify this public Journal
repository; they do not alter scientific results.
