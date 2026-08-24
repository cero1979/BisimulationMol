# Auditing observable behavior in qualitative biological network models

[![Reproducibility](https://github.com/cero1979/BisimulationMol/actions/workflows/reproduce.yml/badge.svg)](https://github.com/cero1979/BisimulationMol/actions/workflows/reproduce.yml)

This repository is the end-to-end reproducibility package for the manuscript:

> *A formal and reproducible framework for auditing observable behavior in
> qualitative biological network models*

The current manuscript is prepared for the **Journal of Bioinformatics and
Computational Biology (JBCB)** using the author-supplied World Scientific class.
Its contribution is a formal and computational framework for reporting the
strongest supported behavioral relation between two finite labeled models under
a declared interface. It does **not** infer experimental
or organism-level biological equivalence from graph structure.

## Reproduction levels

The repository supports three progressively heavier audits. Public input files
are committed for offline use; the fetch targets verify their SHA-256 digests
and contact the source repositories only when a file is absent or invalid.

| Level | Purpose | Command | Additional requirements |
|---|---|---|---|
| Inspect | Read the executed analysis and committed outputs | Open `notebooks/metodologia_multiescala.ipynb` and `results/` | None |
| Core | Re-run formal tests, figures and deterministic tables | `make public-models hpn-data verify` | Python, Graphviz, mCRL2 |
| Full | Recompute CASPOTS scores, notebook, manuscript and upload ZIPs | `make caspots-validation notebook manuscript package` | Core tools, Conda, LaTeX |

`make verify` is the primary reproducibility check. It runs the complete test
suite,
regenerates the scientific outputs and fails if any deterministic tracked
result differs. Runtime measurements are reported but excluded from byte-level
comparison because they depend on hardware.

## Formal and computational safeguards

The study addresses five recurring validity risks:

1. **Computational-method framing.** The title, abstract, research question and
   conclusions now concern model comparison rather than cross-species
   biological equivalence.
2. **Claim discipline.** Every result is stated as a relation between curated
   models conditional on their encoded transitions and observational interface.
3. **Independent formal/software verification.** Six synthetic pairs have
   construction-level ground truth; all strong and weak decisions are
   cross-checked with mCRL2, and the full path is exercised on two public GINsim
   models. These controls do not constitute biological validation.
4. **GIM interface sensitivity.** The same animal/human and Arabidopsis Petri-net
   structures are evaluated at coarse, pathway-resolved and mechanism-resolved
   interfaces. Weak bisimulation at A/B becomes non-comparability at C while
   PN-GDDA remains `0.9976`.
5. **Held-out biological data.** Structure-only representatives of three public
   HPN-DREAM Boolean-network families are fixed without test-value access,
   cross-checked with mCRL2 and scored on reserved mTOR-inhibitor responses.
   The negative specificity result is retained rather than converted into a
   biological-equivalence claim.

A second adversarial pass adds four targeted safeguards:

1. **Direct graphlet comparison.** PN-GDDA is now executed with the published
   151-graphlet/592-slot Holmes catalog on canonical Petri-net encodings and on
   all five native curated pairs. LTS-GDA remains a separate labeled
   reachable-state comparator for heterogeneous input formats.
2. **Update-semantics sensitivity.** Every HPN-DREAM pair is recomputed under a
   global synchronous stress semantics; seven of nine classes persist and two
   weaken from one-way simulation to non-comparability.
3. **Independent simulation oracle.** A separately coded attacker-defender
   game agrees with the production preorder on all 67,600 ordered comparisons
   among every one- and two-state LTS over `{a, tau}`.
4. **Evidence taxonomy.** Formal correctness, software verification,
   executable-model support and independent biological interpretation are
   reported as four separate layers.
5. **Current positioning.** The manuscript now cites direct Petri-net graphlet,
   most-permissive Boolean-network, model-checking and data-informed inference
   literature, with an explicit novelty matrix and stated residual limits.

## Main results

| Evidence item | Result | Supported interpretation |
|---|---|---|
| Six construction-ground-truth pairs | 6/6 formal classes recovered | The implementation distinguishes equivalence, directional simulation and non-comparability |
| Independent mCRL2 oracle | 42/42 synthetic, public-model and HPN strong/weak decisions agree | The principal formal decisions are not specific to the Python implementation |
| Exhaustive simulation-game oracle | 67,600/67,600 ordered pairs agree | Directional simulation has an independent audit on the declared finite universe |
| Direct PN-GDDA audit | Holmes score matches to 12 decimals; PN-GDDA is 2/6 at 0.9 and at most 4/6 over every score threshold | The published structural comparator is executed rather than approximated |
| Native Petri-net comparison | All five PN-GDDA scores are 0.991-1.000 while formal classes range from weak equivalence to non-comparability | Local Petri-net structure does not determine labeled reachable behavior |
| GIM interface sensitivity | A/B: weak bisimulation and `d6=0`; C: neither simulation direction and `d6=0.352941`; PN-GDDA fixed at `0.9976` | Encoded high-level correspondence breaks when organism-specific terminal mechanisms are observed |
| Labelled graphlet comparator | LTS-GDA 4/6 versus summary profile 3/6 | Retaining local labels improves the structural baseline but does not recover branching semantics |
| HPN-DREAM cross-cell comparisons | 18/18 Python/mCRL2 decisions agree | The data-conditioned transition systems are reproducibly classified |
| Asynchronous/synchronous stress | 7/9 classes preserved | Two containment conclusions are explicitly update-semantics dependent |
| Held-out native-cell ranking | Native model first or tied in 2/3 cells; exact `p=0.25` | Compatibility is reproduced; cell specificity is not established |
| Formal relation versus experimental distance | Six one-way and three non-comparable pairs, with direction retained; no scalar class test | The relation is nominal/directional and `n=9` is too small for an ordinal association claim |
| LTS-GDA distance versus experimental distance | Spearman `rho=0.669`; exact `p=0.097` | Stronger observed association, still inconclusive under the exact test |

Machine-readable evidence is in
[`results/synthetic_benchmark.csv`](results/synthetic_benchmark.csv),
[`results/pn_gdda_catalog_validation.json`](results/pn_gdda_catalog_validation.json),
[`results/holmes_pn_gdda_external_validation.json`](results/holmes_pn_gdda_external_validation.json),
[`results/pn_gdda_native_modules.csv`](results/pn_gdda_native_modules.csv),
[`results/pn_gdda_threshold_sensitivity.csv`](results/pn_gdda_threshold_sensitivity.csv),
[`results/mcrl2_synthetic_validation.csv`](results/mcrl2_synthetic_validation.csv),
[`results/simulation_oracle_exhaustive.csv`](results/simulation_oracle_exhaustive.csv),
[`results/gim_interface_sensitivity.csv`](results/gim_interface_sensitivity.csv),
[`results/gim_interface_justification.csv`](results/gim_interface_justification.csv),
[`results/hpn_dream_semantic_sensitivity.csv`](results/hpn_dream_semantic_sensitivity.csv),
[`results/hpn_dream_formal_data_validation.csv`](results/hpn_dream_formal_data_validation.csv)
[`results/hpn_dream_concordance.json`](results/hpn_dream_concordance.json), and
[`results/hpn_dream_caspots_summary.json`](results/hpn_dream_caspots_summary.json).

The synthetic suite recovers all six predeclared formal classes: strong
equivalence, weak equivalence, two directions of one-way simulation, and two
non-comparable cases. On the binary weak-equivalence task:

| Method | Accuracy | False positives | False negatives |
|---|---:|---:|---:|
| Weak bisimulation | 1.000 | 0 | 0 |
| Trace equality at depth 8 | 0.833 | 1 | 0 |
| PN-GDDA-592 at threshold 0.9 | 0.333 | 4 | 0 |
| LTS-GDA at threshold 0.9 | 0.667 | 1 | 1 |
| Structural profile at threshold 0.9 | 0.500 | 2 | 1 |

The direct PN-GDDA implementation generates all 151 connected directed
bipartite graphlets through five nodes and preserves the 592 orbit slots in
Holmes 1.1.1 and 2.0.1.2. On an independently run four-node reference pair, its
score (`0.9872027465870733`) matches Holmes 1.1.1
(`0.987202746587073`) to 12 decimal places. A type- and
direction-preserving automorphism audit yields 576 distinct orbits; this is
reported as a sensitivity analysis and changes no threshold decision. PN-GDDA
calls all six synthetic pairs equivalent at 0.9, including four formal
non-equivalences. No alternative threshold exceeds 4/6 because label mismatch
and label-order swap tie both positive controls at `1.0`. On native nets, even RCD (one-way simulation) scores `1.0000`
and AID (not comparable) scores `0.9907`.

LTS-GDA uses four graphlet-degree orbits and labeled local motifs so that
Petri-net, SBML-qual, GINML and inferred Boolean inputs can be compared in the
common reachable-state representation. It is explicitly a different,
label-aware comparator.

The Python implementation and mCRL2 202607.0 agree on all 24 strong/weak
decisions across six synthetic and six public-model controls. Exact mCRL2
weak-trace outcomes match all 12 predeclared trace controls. The public Boolean
mammalian cell-cycle model yields 826 reachable states and 3,413 edges; the
multilevel p53-Mdm2 model yields 17 states and 26 edges. Source files are stored
with their original URLs and SHA-256 digests.

The independent game oracle additionally agrees on all 67,600 ordered pairs in
the exhaustive small-LTS universe. Synchronous execution reaches only 13 of the
826 asynchronous cell-cycle states and 8 of the 17 p53-Mdm2 states, making the
semantic assumption visible rather than treating it as neutral.

The data-backed analysis adds 284 public CASPOTS networks for BT20, BT549 and
MCF7. Across three shared held-out perturbations, Python and mCRL2 agree on all
18 strong/weak decisions: six cross-cell pairs have one-way simulation and
three are not comparable. The former scalar formal-class coding was removed
because the relation categories are not ordinal and one-way simulation is
directional. The revised output retains three relations in each direction and
three pairs with no simulation, and performs no class/RMSE inferential test.
CASPOTS compatibility RMSE is reproduced twice identically, but native medoids
rank first or tie in only two of three cell lines (exact `p=0.25`). LTS-GDA
distance gives `rho=0.669` but remains inconclusive (`p=0.097`). Synchronous
updating preserves seven classes and changes two one-way simulations to
non-comparability. These negative and sensitivity results delimit the method;
they are not evidence of prognostic performance.

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

The current reference scalability run reached 129 x 145 states and approximately
0.6 s on an Apple M3 Pro. Timings are machine-dependent; model sizes,
relations and classifications are deterministic.

In the central GIM case, the unchanged structures have PN-GDDA `0.9976`.
Interfaces A (coarse) and B (pathway-resolved with terminal fate collapsed) are
weakly bisimilar; Interface C distinguishes apoptosis, SMR induction and the
encoded plant terminal outcome and is non-comparable in both directions. RCD is
a secondary one-way-containment case, while DCE, SPS and AID are supporting
examples. All outputs describe encoded models at declared interfaces only.

## Repository layout

```text
src/concurrent_biomodels.py       Formal engine and curated case-study models
src/gim_interface_analysis.py     Three biologically motivated GIM interfaces
src/pn_gdda.py                    Direct 151/592 PN-GDDA and Holmes audit
src/method_benchmark.py           Synthetic verification, baselines and scaling
src/public_validation.py          SBML/GINML import, AUT export and mCRL2 oracle
src/hpn_dream_validation.py       Blind public-model/data comparison and exact test
src/simulation_oracle.py          Independent game oracle and exhaustive LTS audit
data/public_models/               Hash-verified public GINsim model files
data/hpn_dream/                    Hash-verified HPN-DREAM/CASPOTS families and data
tests/test_method_benchmark.py    Regression and construction-ground-truth tests
tests/test_pn_gdda.py             Catalog, Holmes-score and direct-baseline tests
tests/test_external_validation.py Public-model and independent-oracle tests
tests/test_hpn_dream_validation.py Data integrity, anti-leakage and mCRL2 tests
tests/test_gim_interface_analysis.py GIM definitions, classes and fixed structures
tests/test_simulation_oracle.py    Exhaustive one-/two-state preorder agreement
tests/test_formal_properties.py    Hierarchy, refinement, branching and orientation tests
notebooks/metodologia_multiescala.ipynb
                                  Executed end-to-end analysis notebook
make_figures.py                   Regenerates figures and machine-readable results
results/                          CSV and LaTeX result tables
figs/                             Regenerated figures (git-ignored)
paper/jbcb/main_jbcb.tex          Current manuscript in the official JBCB class
paper/jbcb/references_jbcb.bib    Verified World Scientific bibliography
scripts/build_jbcb_package.py     Builds and checks the clean JBCB upload ZIP
CLAIM_AUDIT_JBCB.md               Evidence status for manuscript claims
REFERENCE_AUDIT_JBCB.md           Per-reference metadata and DOI audit
REPRODUCIBILITY.md                Reviewer-oriented reproduction guide
```

## Quick start

Python 3.10 or newer, system Graphviz and mCRL2 202607.0 are required for the
complete verification. The formal engine and model importers use only the Python
standard library.

```bash
python -m pip install -r requirements.txt
make public-models
make hpn-data
make verify
```

For individual stages, use `make gim-interface`, `make pn-gdda`,
`make external-validation`, `make hpn-validation`, `make test`, `make figures`
or `make notebook`. Expected numeric results,
artifact-to-figure mappings and troubleshooting are documented in
[`REPRODUCIBILITY.md`](REPRODUCIBILITY.md).

`make holmes-pn-gdda` is the optional independent software check. It downloads
Holmes 1.1.1 from its official site, verifies the JAR hash, compiles the included
Java probe, matches all 151 topologies and 592 orbit assignments entry by entry,
and requires 12-decimal agreement with the Python score.

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

The upload archive is `JBCB-1505-revised.zip`. It contains
`main_jbcb.tex`, a prebuilt `bibliography_jbcb.bbl`, the BibTeX database, the
unmodified `ws-jbcb.cls` and `ws-jbcb.bst`, and the six vector figure files.
All eleven files are stored at the ZIP root because Editorial Manager rejects
LaTeX archives containing subfolders. The local preview PDF is deliberately not
inside the ZIP: Editorial Manager warns against uploading a PDF and TeX source
with the same basename. The builder verifies the exact `.bbl`-based upload
source, rejects broken references, box overflow, and nested archive entries,
removes auxiliary files, and checks ZIP integrity.
Code, public models, tests, result tables, and the executed notebook remain in
this repository as the reproducibility package.

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
