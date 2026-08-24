# Reproducibility guide

This repository contains the source models, formal engine, independent
benchmark, tests, executed notebook, generated data and official JBCB LaTeX
source for:

> *A formal and reproducible framework for auditing observable behavior in
> qualitative biological network models*

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
The three fixed GIM observational interfaces and their biological rationale are
defined in `src/concurrent_biomodels.py`; `src/gim_interface_analysis.py`
executes them on unchanged structures and writes both the sensitivity and
justification tables.

## 1. Environment

Requirements:

- Python 3.10 or newer.
- The packages listed in `requirements.txt`.
- System Graphviz (`dot`) for Petri-net and transition-system drawings.
- mCRL2 202607.0 (`ltscompare`) for the independent formal oracle.
- A LaTeX installation with `latexmk` to compile the manuscript.

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
`sudo apt-get install graphviz`. The unmodified official World Scientific class
and bibliography style are stored in `paper/jbcb`, so no journal template
download is needed.

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

Fetch and verify the public HPN-DREAM held-out material with:

```bash
make hpn-data
```

This downloads ten files from public CASPOTS commit `95e3c74`: the merged PKN,
three learning sets, three verified Boolean-network families and three held-out
mTOR-inhibitor tests. Existing files are never trusted without a SHA-256 check.
The historical MCF7 header uses an uppercase inhibitor suffix; only the temporary
CASPOTS input header is normalized, and the original hash-pinned file is retained.

## 3. Verify the formal implementation

```bash
make test
```

The tests require all six construction-ground-truth relations to be recovered,
verify the intended failure modes of direct PN-GDDA, trace, LTS-GDA and structural baselines, retain
the three GIM interface classifications and fixed structures, preserve weak
simulation direction, reject obsolete ordinal class fields, and check deterministic scaling
metadata. They also exhaustively compare the independent simulation game on
67,600 ordered LTS pairs. When `ltscompare` is available, they require full
mCRL2 agreement on the synthetic and public-model controls.

The exact test count may increase as regression coverage is added; a successful
run ends in `OK` with no skips except explicitly optional external tools.

Run the GIM sensitivity analysis alone with:

```bash
make gim-interface
```

It writes `results/gim_interface_sensitivity.csv`,
`results/gim_interface_justification.csv`, and a LaTeX rendering of the
justification table. Expected formal classes are weak bisimulation for A and B
and non-comparability for C; PN-GDDA remains unchanged because the structures
are fixed.

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

Run the external software verification directly with:

```bash
make external-validation
```

This exports AUT files to a temporary directory, checks strong bisimulation,
weak bisimulation and exact weak-trace equivalence with mCRL2, and runs the
independent exhaustive weak-simulation game audit.

Run the exploratory held-out HPN-DREAM comparison with:

```bash
make hpn-validation
```

The command selects one structure-only family medoid without opening a held-out
file, constructs nine cross-cell pair--condition LTS comparisons, requires
Python/mCRL2 agreement, and preserves both simulation directions. Formal classes
are summarized nominally; no ordinal coding or class/RMSE inferential test is
performed. The two predeclared continuous diagnostics retain their exact 216
condition-stratified permutations. The command also writes the nine-pair
asynchronous/synchronous sensitivity comparison.
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

The JBCB manuscript uses these generated outputs:

| Output | Manuscript element | Deterministic? |
|---|---|---|
| `results/synthetic_benchmark.csv` | Table 1 and Section 3.1, including direct PN-GDDA | Yes |
| `results/baseline_accuracy.csv` | Controlled software-benchmark figure, including PN-GDDA and LTS-GDA | Yes |
| `results/pn_gdda_catalog_validation.json` | 151/592 catalog audit, Holmes reference score and 576-orbit sensitivity | Yes |
| `results/holmes_pn_gdda_external_validation.json` | Score produced by the hash-verified Holmes 1.1.1 JAR | Yes |
| `results/pn_gdda_native_modules.csv` | Direct PN-GDDA on five original curated net pairs | Yes |
| `results/pn_gdda_threshold_sensitivity.csv` | Every attainable synthetic PN-GDDA score-threshold decision | Yes |
| `results/mcrl2_synthetic_validation.csv` | Independent oracle on six synthetic pairs | Yes |
| `results/simulation_oracle_exhaustive.csv` | Exhaustive one-/two-state simulation-game audit | Yes |
| `results/public_models.csv` | Public sources, sizes, conditions and hashes | Yes |
| `results/public_model_validation.csv` | Six public-model controls and mCRL2 results | Yes |
| `results/public_model_semantic_sensitivity.csv` | Public asynchronous/synchronous reachability | Yes |
| `results/gim_interface_sensitivity.csv` | Central A/B/C GIM result table and figure | Yes |
| `results/gim_interface_justification.csv` | Biological rationale and literature keys for GIM observables | Yes |
| `results/gim_interface_justification.tex` | Generated LaTeX rendering of the rationale audit | Yes |
| `results/hpn_dream_medoids.csv` | Blind family selection, hashes and anti-leakage flag | Yes |
| `results/hpn_dream_formal_data_validation.csv` | Nine distinct-model/data comparisons and mCRL2 results | Yes |
| `results/hpn_dream_concordance.json` | Nominal direction summaries and exact continuous-diagnostic tests; no scalar class test | Yes |
| `results/hpn_dream_semantic_sensitivity.csv` | Nine HPN asynchronous/synchronous class comparisons | Yes |
| `results/hpn_dream_caspots_rmse.csv` | Repeated held-out medoid and family-oracle scores | Yes |
| `results/hpn_dream_caspots_summary.json` | Native-versus-cross specificity test | Yes |
| `figs/Fig1.pdf` | Fig. 1, six-stage workflow | Yes |
| `figs/Fig2.pdf` | Central GIM biological abstraction and interface-sensitivity result | Yes |
| `figs/FigS1a.pdf`, `figs/FigS1b.pdf` | Full GIM Petri nets retained in the appendix | Yes |
| `figs/Fig3.pdf` | Controlled software/formal benchmark | Yes |
| `results/scalability_structure.csv` | State/relation sizes in Section 3.3 | Yes |
| `results/scalability_runtime.csv` | Reference timing series described in Section 3.3 | No, machine-dependent |
| `figs/Fig4.pdf` | Repository-only scalability plot | No, timing panel is machine-dependent |
| `results/phase6_comparisons.csv` | Table 4, curated model-pair relations | Yes |
| `figs/Fig5a.pdf`, `figs/Fig5b.pdf` | Repository-only GIM reachability systems | Yes |
| `figs/Fig6a.pdf`, `figs/Fig6b.pdf` | Repository-only RCD Petri nets | Yes |
| `figs/Fig7a.pdf`, `figs/Fig7b.pdf` | Repository-only robustness and null plots | Yes |
| `figs/Fig8.pdf` | Exploratory direction-preserving HPN held-out display | Yes |

The command also regenerates PNG previews and provenance, interface,
conservation and generalization diagnostics retained in the repository. Those
additional outputs support auditing but do not enlarge the revised paper's
biological claim.

## 5. Execute the notebook

```bash
make notebook
```

The notebook is first updated idempotently and then executed in place. Cells
tagged `netmahib-benchmark` perform the synthetic controls, three-interface GIM
experiment, public GINsim controls, exploratory HPN-DREAM check, direct
PN-GDDA/Holmes audit, graphlet/trace baselines, exhaustive simulation audit,
semantic sensitivity and runtime scaling. The committed notebook includes outputs
so a reviewer can inspect the complete run without executing code first.

## 6. Check deterministic outputs

```bash
make verify
```

This regenerates `results/` and compares all deterministic tracked outputs with
the committed versions. Runtime measurements are excluded from the byte-level
check because performance cannot be identical across processors. The benchmark
still asserts deterministic model sizes, relation sizes and formal outcomes.

## 7. Compile the JBCB manuscript

```bash
make manuscript
```

Equivalent manual command:

```bash
cd paper/jbcb
latexmk -pdf -interaction=nonstopmode -halt-on-error main_jbcb.tex
```

The expected output is `paper/jbcb/main_jbcb.pdf`. The source uses the
unmodified official `ws-jbcb` class, class-native theorem environments,
first-appearance numeric citations through `ws-jbcb.bst`, American English, and
an abstract checked against the journal limit by `tools/check_jbcb_abstract.py`.

## 8. Build the submission ZIP

```bash
make package
```

This writes and verifies:

```text
JBCB-1505-revised.zip
```

The ZIP contains the main source, a prebuilt `.bbl`, the BibTeX database,
official JBCB class and style, and six vector files composing four main figures
and two detailed appendix figures. All eleven entries are at the archive root;
no directory entries or subfolders are
permitted by Editorial Manager. The compiled preview PDF remains outside the
ZIP to avoid a duplicate basename with the main TeX source. Build auxiliaries
and logs are removed. The complete reproducibility materials remain in the
repository at the public URL stated in the manuscript. The exact flat source set
is also available in `submission_jbcb_revision/`.
To verify the archive independently:

```bash
unzip JBCB-1505-revised.zip -d /tmp/jbcb-check
cd /tmp/jbcb-check
latexmk -pdf -interaction=nonstopmode -halt-on-error main_jbcb.tex
```

## 9. Interpretation boundary

Reproduction establishes that direct PN-GDDA reconstructs the published/Holmes
151/592 catalog and reference score, that two formal implementations return the
reported strong and weak relations, that the public-model import path recovers
the controlled transformations, that the production simulation preorder agrees
with its game oracle on the declared finite universe, and that GIM changes from
weak bisimulation at A/B to non-comparability at C without structural changes.
It also reproduces the reported HPN-DREAM held-out compatibility scores. Those
data fail to establish native-cell specificity (`p=0.25`) or a significant
LTS-GDA/data association (`p=0.097`). No formal-class/data scalar test is
reported because directional relations do not define a justified ordinal scale.
Direct PN-GDDA produces four construction-level false positives at the declared
0.9 diagnostic threshold, which demonstrates only that it answers a different
question. Two of nine HPN classes change under synchronous updating.
Reproduction therefore does not validate organism-level equivalence, kinetic
completeness or prognostic utility. Model definitions, provenance, interfaces
and negative results are exposed so those assumptions can be audited or
replaced.

The repository uses the same four-layer evidence vocabulary as the manuscript:

| Layer | Reproducible artifacts | Boundary |
|---|---|---|
| I Formal correctness | Definitions, proofs and formal-property tests | Mathematical claims only |
| II Software/implementation verification | Constructed controls, mCRL2, game oracle and regression tests | Tested computation, not biology |
| III Executable-model support | Hashes, import controls, provenance and explicit update semantics | Auditable model origin/assumptions, not experimental calibration |
| IV Biological interpretation | Verified DDR literature and exploratory HPN held-out data | Plausibility or preliminary confrontation with data, not organism-level equivalence |

## 10. Troubleshooting

- If a graph is blank or `pydot` fails, verify `dot -V`.
- If external validation cannot start, verify `ltscompare --version` or set
  `MCRL2_LTSCOMPARE` to the executable path.
- If `latexmk` cannot find the class, compile from `paper/jbcb`; the required
  `ws-jbcb.cls` and `ws-jbcb.bst` files are local.
- If `make verify` reports only timing differences, confirm that the runtime CSV
  is excluded by the current Makefile pathspec.
- If a deterministic CSV differs, run `make test` first and report the Python
  version and platform when opening an issue.
