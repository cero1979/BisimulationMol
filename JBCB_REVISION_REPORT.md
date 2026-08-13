# JBCB Revision Report

Date: 2026-08-13. Branch: `codex/jbcb-revision`.

## A. Baseline

The primary scientific source was the strengthened working JMCS file
`submission_jmcs/main.tex` (21 compiled pages, 7,837 TeX-count words). The
NetMAHIB source `submission/netmahib_latex_flat/main.tex` (23 pages) supplied
biological narrative context only. Both were preserved. The author-supplied
`jbcb-2e.zip` was hash-audited before its exact class and style were imported.

## B. Template compliance

- Unmodified `ws-jbcb.cls` 2026/05/18 v1.5g and `ws-jbcb.bst` are used.
- The title renders in approximately two lines; no invented ORCID or publisher
  dates appear.
- The abstract has 184 words, no citation, URL, or displayed equation.
- Prose is American English; six semicolon-separated keywords and no MSC remain.
- Citations are superscript numeric, ordered by first appearance, and placed
  after punctuation.
- Figures have captions below; tables use class-native captions above.
- The Editorial Manager archive contains ten root-level files and no subfolders;
  it supplies a prebuilt `.bbl` and omits the compiled PDF to avoid a duplicate
  basename with the primary TeX source.
- Class-native theorem/proof environments are used without `amsthm`.
- The only compile warning is the `hyperref` page-height warning also induced by
  the official template's load order; there are no box, citation, or reference
  warnings.

## C. Narrative changes

The manuscript now opens with the biological-model comparison problem, explains
why topology and finite traces omit executable branching information, then
introduces the formal framework as the solution. Four contributions replace the
longer theory-centered list. Methods and results are integrated to avoid
repetition, and the discussion closes on model auditing at a declared
observational resolution.

## D. Mathematical content preserved

The final source retains the labeled Petri-net and finite-LTS definitions,
`tau` closure and weak targets, directed weak simulation, strong/weak
bisimulation, exact and truncated weak languages, the classifier, exclusive
reporting proposition, greatest-fixed-point theorem and proof, resource bound,
relation hierarchy, controlled silent refinement, label-blind limitation, and
the equal-trace/different-branching example.

## E. Mathematical content changed

Statements and assumptions were not weakened. Proof prose was compressed while
preserving the invariant and fixed-point steps. American terminology replaced
British spelling. Three tests were added for mutual simulation without
bisimulation, truncated versus exact traces, and zero-or-more `tau` closure.
Human proof sign-off remains required in `FORMAL_RESULTS_AUDIT_JBCB.md`.

## F. Biological content

Public GINsim models and HPN-DREAM/CASPOTS now appear as central applications,
not late supplements. The GIM animal/Arabidopsis Petri nets remain visible as
the principal interface-dependence example. Other curated modules are compressed
into one table. Full GIM LTS, RCD, robustness, and scaling plots remain in the
repository rather than duplicating evidence in the article.

## G. Numerical results

No value changed. The final text retains 6/6, 5/6, 4/6, 3/6, and 2/6 benchmark
decisions; 151 graphlets, 592 published slots, 576 sensitivity orbits, and the
12-decimal Holmes match; 260 LTSs and 67,600 comparisons; 42 Python/mCRL2
decisions; GINsim sizes 826/3,413 and 17/26; HPN family sizes 72/191/21; nine
pair-condition comparisons; rho/p values 0.091/0.111, -0.596/0.556, and
0.669/0.097; native specificity p=0.25; and largest scaling size 129 x 145 with
18,705 candidate pairs.

## H. Reproducibility

Executed commands included baseline compilation, abstract/language checks,
`make verify` with mCRL2 202607.0, clean manuscript compilation, and
`make jbcb-package`. The final flat ZIP was also extracted and compiled in an
independent temporary directory. The final regression passed 35/35 tests and regenerated all
tracked deterministic results byte-for-byte. Details and full output are in
`JBCB_RESULT_REGRESSION.md` and `audit/jbcb_final/`.

## I. References

Twenty DOI-bearing cited records were resolved through Crossref; Milner's book
was checked by ISBN. Li et al. (2006) and Yizengaw (2026) were added because they
directly ground biological Petri-net structure and asynchronous Boolean-network
reachability. Three other potentially relevant JBCB papers were audited and not
cited because their quantitative or pathway-validation scope was peripheral.
The final bibliography contains 21 cited entries.

## J. Page budget

The direct conversion occupied 27 pages; integrated and compressed passes
occupied 20 and 18. The final candidate is 17 pages. A redundant conceptual
table and the machine-dependent runtime plot were removed; all principal formal
and biological evidence remains. Reducing to 15 would require moving a proof or
principal validation figure and is not recommended without editorial feedback.

## K. Language

Manuscript prose was converted consistently to American English (`behavior`,
`labeled`, `modeling`, `catalog`, `relabeling`). The automated checker reports
zero findings. Published titles in the BibTeX database retain original spelling.

## L. AI disclosure

The supplied JBCB template has no AI section, and the exact online JBCB policy
could not be retrieved through the publisher's web protection. A truthful
disclosure covering language, organization, format adaptation, and
reproducibility checks remains in the PDF. The author must approve its wording
and confirm portal placement as described in `AI_DISCLOSURE_QUERY_JBCB.md`.

## M. Remaining risks

1. External empirical power remains limited to nine HPN observations and three
   cell lines; the article correctly reports inconclusive exact tests.
2. Curated Petri nets are model-level illustrations without independent
   biological validation.
3. Explicit-state performance is demonstrated only to 145 states, not genomic
   scale.
4. The final length is two pages above the 15-page free allowance stated in the
   supplied template.
5. Author confirmation is still required for proofs, disclosure wording,
   affiliation/declarations, and cover-letter exclusivity.

No submission, remote push, release, or tag was performed.
