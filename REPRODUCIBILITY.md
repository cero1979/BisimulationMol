# Reproducibility guide

This repository contains the source models, formal engine, independent
benchmark, tests, executed notebook, generated data and Springer Nature LaTeX
source for:

> *Auditing observable behaviour in qualitative biological network models: a
> reproducible Petri-net framework*

The analysis runs offline after the public GINsim and HPN-DREAM/CASPOTS source
files have been fetched once.
No API, confidential dataset or database credential is needed. The curated biological models are encoded in
`src/concurrent_biomodels.py`; the independent synthetic models are generated
deterministically in `src/method_benchmark.py`. Public GINsim models are stored
under `data/public_models` with source URLs and SHA-256 checksums declared in
`src/public_validation.py`.
The three Boolean-network families, learning sets, held-out mTOR-inhibitor data
and merged prior-knowledge network are stored under `data/hpn_dream`; their
historical commit and SHA-256 registry are fixed in
`scripts/fetch_hpn_dream.py`.
The independent simulation audit is implemented in
`src/simulation_oracle.py`; it enumerates the complete declared small-LTS
universe without external dependencies.
Direct PN-GDDA is implemented in `src/pn_gdda.py`; it generates the complete
151-topology catalog, preserves the published/Holmes 592 orbit slots and emits
a separate 576-orbit automorphism sensitivity audit.

## 1. Environment

Requirements:

- Python 3.10 or newer.
- The packages listed in `requirements.txt`.
- System Graphviz (`dot`) for Petri-net and transition-system drawings.
- mCRL2 202607.0 (`ltscompare`) for the independent formal oracle.
- A LaTeX installation with `latexmk` and BibTeX to compile the manuscript.

The optional held-out CASPOTS score reproduction uses the separate
`environment-hpn.yml` specification with Python 3.11, CASPO 4.0.3, Clingo 5.8.0,
NuSMV 2.6.0 and CASPOTS commit `cee54b8`. Generated scores are included in the
repository, so this heavier environment is not required to inspect or plot them.

Set up with pip:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

For the independent CASPOTS RMSE audit:

```bash
conda env create -f environment-hpn.yml
conda run -n bisimulationmol-hpn python scripts/run_caspots_hpn_validation.py --repeats 2
```

On macOS, install Graphviz with `brew install graphviz`. On Debian/Ubuntu, use
`sudo apt-get install graphviz`. The Springer class and bibliography style are
stored in `paper/netmahib`, so no journal template download is needed.

The analysis was validated with the official mCRL2 202607.0 release. Set
`MCRL2_LTSCOMPARE=/path/to/ltscompare` if it is not on `PATH`. The CI workflow
downloads the fixed x86-64 Debian asset and verifies SHA-256
`00cb4c347638b3a418fb67c9d67b8d2bf2245e10d4affa4cd993b1c357bde969`.

## 2. Fetch and verify public models

```bash
make public-models
```

The command downloads the public mammalian cell-cycle SBML-qual model and
p53-Mdm2 GINML model only when absent, and refuses files whose SHA-256 differs
from the manifest.

Fetch and verify the independent HPN-DREAM validation material with:

```bash
make hpn-data
```

This downloads ten files from public CASPOTS commit `95e3c74`: the merged PKN,
three learning sets, three verified Boolean-network families and three held-out
mTOR-inhibitor tests. Existing files are never trusted without a SHA-256 check.
The historical MCF7 header uses an uppercase inhibitor suffix; only the temporary
CASPOTS input header is normalized, and the original hash-pinned file is retained.

## 3. Validate the formal implementation

```bash
make test
```

The tests require all six construction-ground-truth relations to be recovered,
verify the intended failure modes of direct PN-GDDA, trace, LTS-GDA and structural baselines, retain
the biological-case regression results, and check deterministic scaling
metadata. They also exhaustively compare the independent simulation game on
67,600 ordered LTS pairs. When `ltscompare` is available, they require full
mCRL2 agreement on the synthetic and public-model controls.

Expected summary:

```text
Ran 25 tests
OK
```

Run the direct graphlet audit alone with:

```bash
make pn-gdda
```

It prints the 151/592 published catalog, the 151/576 automorphism sensitivity
catalog and both scores for each native animal/plant Petri-net pair. The Holmes
reference comparison and JAR hashes are stored in
`results/pn_gdda_catalog_validation.json`.

With a JDK and network access, execute the external Holmes binary itself:

```bash
make holmes-pn-gdda
```

The command downloads the official Holmes 1.1.1 archive, verifies JAR SHA-256
`1747a9798c074a4e8a560cded9396ec3d0be05af2d948953c7730d5e623f044c`,
compiles `scripts/HolmesPnGddaProbe.java` in a temporary directory and writes
`results/holmes_pn_gdda_external_validation.json`. The probe verifies every one
of the 151 topology signatures and 592 root assignments before comparing the
reference score. Nothing from Holmes is redistributed in this repository.

Run the external validation directly with:

```bash
make external-validation
```

This exports AUT files to a temporary directory, checks strong bisimulation,
weak bisimulation and exact weak-trace equivalence with mCRL2, and runs the
independent exhaustive weak-simulation game audit.

Run the blind HPN-DREAM comparison with:

```bash
make hpn-validation
```

The command selects one structure-only family medoid without opening a held-out
file, constructs nine cross-cell pair--condition LTS comparisons, requires
Python/mCRL2 agreement and executes the exact 216-permutation class/data test.
It also writes the nine-pair asynchronous/synchronous sensitivity comparison.
The CASPOTS environment command `make caspots-validation` recomputes 12 held-out
compatibility scores twice and aborts if any optimum differs between repetitions.

To print the classifications directly:

```bash
python src/method_benchmark.py
python src/concurrent_biomodels.py
```

## 4. Regenerate figures and result tables

```bash
make figures
```

The NetMAHIB manuscript uses these generated outputs:

| Output | Manuscript element | Deterministic? |
|---|---|---|
| `results/synthetic_benchmark.csv` | Table 2 source and Section 3.1, including direct PN-GDDA | Yes |
| `results/baseline_accuracy.csv` | Table 3 and Fig. 3, including PN-GDDA and LTS-GDA | Yes |
| `results/pn_gdda_catalog_validation.json` | 151/592 catalog audit, Holmes reference score and 576-orbit sensitivity | Yes |
| `results/holmes_pn_gdda_external_validation.json` | Score produced by the hash-verified Holmes 1.1.1 JAR | Yes |
| `results/pn_gdda_native_modules.csv` | Direct PN-GDDA on five original curated net pairs | Yes |
| `results/pn_gdda_threshold_sensitivity.csv` | Every attainable synthetic PN-GDDA score-threshold decision | Yes |
| `results/mcrl2_synthetic_validation.csv` | Independent oracle on six synthetic pairs | Yes |
| `results/simulation_oracle_exhaustive.csv` | Exhaustive one-/two-state simulation-game audit | Yes |
| `results/public_models.csv` | Public sources, sizes, conditions and hashes | Yes |
| `results/public_model_validation.csv` | Six public-model controls and mCRL2 results | Yes |
| `results/public_model_semantic_sensitivity.csv` | Public asynchronous/synchronous reachability | Yes |
| `results/hpn_dream_medoids.csv` | Blind family selection, hashes and anti-leakage flag | Yes |
| `results/hpn_dream_formal_data_validation.csv` | Nine distinct-model/data comparisons and mCRL2 results | Yes |
| `results/hpn_dream_concordance.json` | Exact class/data permutation test | Yes |
| `results/hpn_dream_semantic_sensitivity.csv` | Nine HPN asynchronous/synchronous class comparisons | Yes |
| `results/hpn_dream_caspots_rmse.csv` | Repeated held-out medoid and family-oracle scores | Yes |
| `results/hpn_dream_caspots_summary.json` | Native-versus-cross specificity test | Yes |
| `figs/Fig1.pdf` | Fig. 1, six-stage workflow | Yes |
| `figs/Fig2a.pdf`, `figs/Fig2b.pdf` | Fig. 2, GIM Petri nets | Yes |
| `figs/Fig3.pdf` | Fig. 3, benchmark validation | Yes |
| `results/scalability_structure.csv` | State/relation sizes in Section 3.2 | Yes |
| `results/scalability_runtime.csv` | Reference timing series for Fig. 4 | No, machine-dependent |
| `figs/Fig4.pdf` | Fig. 4, scalability | No, timing panel is machine-dependent |
| `results/phase6_comparisons.csv` | Curated case-study relation table | Yes |
| `figs/Fig5a.pdf`, `figs/Fig5b.pdf` | Fig. 5, GIM reachability systems | Yes |
| `figs/Fig6a.pdf`, `figs/Fig6b.pdf` | Fig. 6, RCD Petri nets | Yes |
| `figs/Fig7a.pdf`, `figs/Fig7b.pdf` | Fig. 7, robustness and null reference | Yes |
| `figs/Fig8.pdf` | Fig. 8, blinded held-out validation | Yes |

The command also regenerates PNG previews and the earlier provenance,
interface, conservation and generalization diagnostics retained in the
repository. Those additional outputs support auditing but are not used to
enlarge the revised paper's biological claim.

## 5. Execute the notebook

```bash
make notebook
```

The notebook is executed in place. Cells tagged `netmahib-benchmark` perform the
synthetic controls, public GINsim controls, blinded HPN-DREAM validation,
direct PN-GDDA/Holmes audit, graphlet/trace baselines, exhaustive simulation
audit, semantic sensitivity and runtime scaling. The committed notebook includes outputs
so a reviewer can inspect the complete run without executing code first.

## 6. Check deterministic outputs

```bash
make verify
```

This regenerates `results/` and compares all deterministic tracked outputs with
the committed versions. Runtime measurements are excluded from the byte-level
check because performance cannot be identical across processors. The benchmark
still asserts deterministic model sizes, relation sizes and formal outcomes.

## 7. Compile the NetMAHIB manuscript

```bash
make manuscript
```

Equivalent manual command:

```bash
cd paper/netmahib
latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex
```

The expected output is `paper/netmahib/main.pdf`. The source uses the Springer
Nature `sn-jnl` class with the author-year mathematics and physics bibliography
style, a 150-250 word abstract, six keywords and the required availability and
declaration statements.

## 8. Build the submission ZIPs

```bash
make package
```

This writes:

```text
submission/netmahib_latex_flat.zip
submission/netmahib_reproducibility.zip
```

The LaTeX ZIP has no nested source paths. It contains exactly the main source,
Springer class, bibliography style, BibTeX database, generated BBL and the 12
vector artwork files that compose the eight figures referenced by the article.
The reproducibility ZIP preserves repository paths and contains code, public
models, HPN-DREAM data, tests, generated tables, both environment specifications,
workflow and executed notebook.
To verify the archive independently:

```bash
unzip submission/netmahib_latex_flat.zip -d /tmp/netmahib-check
cd /tmp/netmahib-check
latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex
```

## 9. Interpretation boundary

Reproduction establishes that direct PN-GDDA reconstructs the published/Holmes
151/592 catalog and reference score, that two formal implementations return the reported strong
and weak relations, that the public-model import path recovers the controlled
transformations, that the production simulation preorder agrees with its game
oracle on the declared finite universe, and that the HPN-DREAM medoids attain the reported held-out
compatibility scores. The same data also fail to establish native-cell
specificity (`p=0.25`), formal-class/data concordance (`p=0.111`) or a
significant LTS-GDA/data association (`p=0.097`). Direct PN-GDDA also produces
four synthetic false positives at the declared 0.9 diagnostic threshold. Two of nine directional
classes change under synchronous updating. Reproduction
therefore does not validate organism-level equivalence, kinetic completeness or
prognostic utility. Model definitions, provenance, interfaces and negative
results are exposed so those assumptions can be audited or replaced.

## 10. Troubleshooting

- If a graph is blank or `pydot` fails, verify `dot -V`.
- If external validation cannot start, verify `ltscompare --version` or set
  `MCRL2_LTSCOMPARE` to the executable path.
- If `latexmk` cannot find a class, compile from `paper/netmahib`; the required
  `sn-jnl.cls` is local.
- If `make verify` reports only timing differences, confirm that the runtime CSV
  is excluded by the current Makefile pathspec.
- If a deterministic CSV differs, run `make test` first and report the Python
  version and platform when opening an issue.
