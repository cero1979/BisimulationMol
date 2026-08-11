# JMCS revision report

Revision date: 2026-08-11

Working branch: `codex/jmcs-revision`

Submission status: **human mathematical and declaration review required**

## A. Files changed

- JMCS source: `paper/jmcs/main.tex`, `references.bib`,
  `references_jmcs.tex`, official template/class/logo and compiled `main.pdf`.
- Formal tests: `tests/test_formal_properties.py` and the mCRL2 availability
  guard in `tests/test_hpn_dream_validation.py`.
- Reproduction/build: `Makefile`, `README.md`, `REPRODUCIBILITY.md`, `.gitignore`,
  `scripts/build_jmcs_package.py`, and the executed notebook.
- Audits/delivery: `JMCS_BASELINE_AUDIT.md`, `REFERENCE_AUDIT.md`,
  `CLAIM_AUDIT.md`, `AI_USE_LOG.md`, `COVER_LETTER_JMCS.md`, this report,
  `JMCS_REVISION.diff`, final logs and `submission_jmcs/`.
- The official `ISRP.cls` and `jmcs.jpg` files were copied from the supplied
  template and left unmodified.

## B. Structural changes

| Previous NetMAHIB section | JMCS section |
|---|---|
| Introduction led by biological model comparison | Introduction led by the formal input/output problem and comparison layers |
| Methods: problem, Petri nets and behavioural relations | 2. Mathematical framework: seven definitions, classifier, fixed-point operators and formal properties |
| Methods: synthetic/public validation and baselines | 3. Algorithms and computational validation |
| Methods: GINsim, HPN-DREAM and curated biology | 4. Applications to qualitative biological network models |
| Results dispersed by data source | 5. Results ordered from construction-level and independent validation to applications |
| Discussion: establishes/does not establish/practical use | 6. Discussion: semantic hierarchy; structure/traces/branching; interfaces; independent evidence; biological and computational limits |
| Springer statements block | JMCS-specific availability, funding, interests, ethics, contributions and AI declaration |

All eight original figure environments remain. The 12 vector panels are reused
without AI modification.

## C. Mathematical additions

| Item | Statement/type | Proof added | Dependencies | AUTHOR_PROOF_REVIEW_REQUIRED |
|---|---|---|---|---|
| Definition 2.1 | Labelled place/transition net and firing semantics; standard | No | Murata; implementation | NO |
| Definition 2.2 | Finite reachable LTS; standard | No | Definition 2.1 | NO |
| Definition 2.3 | Silent closure and weak target sets; standard convention | No | Definition 2.2 | NO |
| Definition 2.4 | Oriented weak simulation; standard | No | Definition 2.3 | NO |
| Definition 2.5 | Weak and strong bisimulation; standard | No | Definitions 2.3-2.4 | NO |
| Definition 2.6 | Exact/truncated weak traces and diagnostic distance | No | Definition 2.3 | NO |
| Definition 2.7 | Framework-specific graded reporting classifier | No | Definitions 2.4-2.5 | NO |
| Proposition 2.8 | Classifier reports exactly one class | Complete Boolean case split | Definition 2.7 | YES |
| Theorem 2.9 | Monotone transfer operators; finite deletion returns their greatest fixed points | Complete invariant/fixed-point proof | Definitions 2.4-2.5; actual code loop | YES |
| Remark 2.10 | Parameterized resource bound, without invented tight runtime complexity | Not applicable | Code data structures | NO |
| Proposition 2.11 | Strong -> weak -> mutual simulation -> exact finite weak-trace equality; converses fail | Transfer inclusions, path induction and counterexamples | Definitions 2.3-2.6 | YES |
| Proposition 2.12 | Controlled observable-then-silent edge subdivision preserves weak, generally not strong, bisimilarity | Explicit witness relation and contradiction | Benchmark construction | YES |
| Proposition 2.13 | Relabelling-invariant label-blind structure cannot characterize labelled behaviour | Minimal two-state counterexample | Labelled semantics | YES |
| Example 2.14 | Equal exact traces do not imply bisimulation or mutual simulation | Explicit branching and orientation argument | Proposition 2.11 | YES |
| Algorithms 2.15-2.18 | Reachability, weak targets, in-place relation deletion and graded classification | Pseudocode follows implementation | `src/` engine | NO |

The formal relations and fixed-point technique are not claimed as new. The
contribution claimed is their explicit integration, reporting rule, audited
implementation and cross-format application.

## D. Claims preserved

- Synthetic results: 6/6 weak bisimulation, 5/6 trace, 4/6 LTS-GDA, 3/6
  structural profile and 2/6 PN-GDDA on the declared binary task.
- Independent game: 67,600/67,600 ordered small-LTS comparisons.
- Python/mCRL2: all 42 reported strong/weak decisions agree.
- PN-GDDA: 151 graphlets, 592 published slots, 576-orbit sensitivity and Holmes
  agreement to 12 decimals.
- HPN: family sizes 72/191/21, medoids 24/137/9, nine comparisons,
  `rho=0.669`, exact `p=0.097`, and native-specificity `p=0.25`.
- Public and curated model state counts, classes and all negative conclusions.

## E. Claims changed

- Title and framing changed from a bioinformatics audit to a formal/computational
  model-comparison framework; no biological result was strengthened.
- The scalability phrase changed from approximately 0.54 s to approximately
  0.6 s after a fresh machine-dependent run. State counts, candidate pairs and
  formal classes are unchanged.
- Bibliographic metadata were corrected only after DOI or publisher verification.
- Claims of organism-level equivalence, prognosis or cell specificity remain
  explicitly excluded.

## F. Reproducibility

| Command/check | Result |
|---|---|
| Baseline LaTeX and tests | 23 pages; 25 tests discovered, 23 pass, 1 skip, 1 mCRL2 error before availability guard |
| `MCRL2_LTSCOMPARE=... make verify` | 32/32 tests pass; figures/results regenerated; deterministic result diff clean |
| `make external-validation hpn-validation holmes-pn-gdda pn-gdda analysis` | Passed; public hashes, 67,600 game pairs, HPN, Holmes and curated cases reproduced |
| `make notebook` | Completed in place with mCRL2 202607.0 |
| `latexmk -pdf ... paper/jmcs/main.tex` | 21 pages; no undefined citation/reference or box warning |
| Clean-package compile and ZIP integrity | Passed; 17 required files, no build auxiliary files |
| PDF rendering/visual inspection | All 21 pages inspected; eight figure environments visible; no clipping or overlap found |

The official class emits four `incorrect series value mc` font warnings. They
originate in unmodified `ISRP.cls`; there are no manuscript-source warnings. A
non-fatal pandas warning notes `numexpr 2.10.1` versus the optional 2.10.2 level;
all deterministic result files nevertheless matched.

## G. References

- 34 database entries were audited; 29 cited entries are printed alphabetically.
- 30 DOI-bearing records resolve; books/proceedings without DOI were checked
  against publisher, institutional or author-hosted records.
- Author names, entry types, one year/key, titles, pages and ISBNs were corrected
  where documented in `REFERENCE_AUDIT.md`.
- Five uncited entries were excluded from the printed list. No placeholder or
  unresolved citation remains.

## H. JMCS compliance

- Official supplied `ISRP.cls` in `[JMCS,submit]` mode; English manuscript; A4 PDF.
- Formal-first title, abstract, introduction and conclusion; real MSC2020 codes
  68Q85, 68Q60 and 68Q55.
- Journal theorem environments, numbered equations, `\eqref`, `\ref` and
  `\cite`; alphabetical manual references and DOI hyperlinks.
- Funding, interests, ethics, contributions, data/code availability and exact
  `Declaration of AI Use` section immediately before References.
- Clean self-contained source/PDF ZIP compiled independently after extraction.

## I. AI-policy compliance

Codex performed targeted editorial changes, code/tests, proof drafting,
reference checks, LaTeX migration and reproducibility execution. It did not
generate or edit figures, change thresholds, select data, suppress negative
results or claim scientific authorship. Details are in `AI_USE_LOG.md`.

**Author action required:** review every proof flagged above, confirm all personal
and declaration metadata, and approve the AI statement. The package is a review
candidate, not authorization to submit before those checks.

## J. Remaining risks

1. JMCS may regard the underlying behavioural relations as standard and judge
   the integration/application contribution insufficiently novel.
2. Every Codex-assisted proof still requires line-by-line author verification.
3. Empirical validation is small and inconclusive (`p=0.097`, `p=0.25`); it
   cannot support prognostic or cell-specific claims.
4. Explicit reachability is demonstrated only through 145 states and 18,705
   candidate pairs, not genome-scale systems.
5. Application conclusions depend on encoded models, update semantics and the
   declared observational interface.
6. JMCS's AI-screening policy creates editorial risk even with disclosure;
   preserve the log and ensure the final prose reflects the author's own review.
7. The official class font warnings should be reported to the editorial office
   only if its submission checker treats them as blocking.
