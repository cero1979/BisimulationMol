# Changes from Supplied R1 to R2

## Mathematical corrections/clarifications
No true mathematical or directional defect was found in the audited claims.
Example 1 now gives the exact finite language, five-pair simulation witness,
two failed successor pairs, and explicit quantifier explanation. Proposition 2
has a three-witness table and expanded middle-converse argument. The fixed-point
theorem is unchanged, including in-place deletion semantics.

## JBCB repositioning
The biological model/readout question now precedes mathematical machinery.
Order: introduction; biological models/interfaces; computational method;
GIM main results; curated supporting cases; exploratory HPN; short verification;
discussion; conclusion; mathematical appendix; detailed Petri nets.

## Title/abstract/introduction
Old: A formal and reproducible framework for auditing observable behavior in
qualitative biological network models.

Chosen: Locating resolution-dependent behavioral correspondence in qualitative
DNA-damage response models.

Alternatives considered:
- Observational resolution in cross-model DNA-damage response comparisons.
- When similar DNA-damage networks cease to match observable behavior.
- Structural similarity and resolution-dependent behavior in DNA-damage models.

The chosen title names the concrete models and conditional method without
implying a universal result. Abstract and introduction were rewritten, not patched.
The abstract omits 6/6, 42, 67,600, and HPN p=0.25.

## GIM narrative
Five focused result subsections distinguish fixed structure, A, B, C, and what
changing observability means. Generated results retain PN-GDDA 0.9976 and A/B
weak bisimilarity versus C non-comparability. The boundary is only within the
declared interface family; it is not a globally minimal experimental scale.

## Validation relocation
Definitions and algorithm stay in the main method. Full mathematical proofs
stay in Appendix A. Detailed synthetic, PN-GDDA, mCRL2, public-model and scaling
validation moves to a separately compiled supplement. No analysis was deleted.

## Main-text validation summary added before resubmission
Section 7 now retains a compact Table 4 with five check/basis/outcome rows:
constructed classes, external mCRL2 equivalence, independent directional audit,
exhaustive finite testing, and the Holmes structural-score comparison. Scope
limits distinguish finite verification from proof and biological evidence.
Detailed outputs remain supplementary; no numerical outcome was changed.
The hierarchy-witness table becomes Table 5. Response items R2.2/R2.9 and the
reviewer matrix are synchronized. Fixed-width columns preserve legibility in
the journal class, and duplicate Appendix prefixes were corrected.
The manuscript is 22 pages with five tables; the response remains seven pages.
Both manuscript submission archives were rebuilt and clean-compiled.

## HPN reframing
A short secondary exploratory section remains in the article. Full methods,
medoid table, direction-preserving plot, and negative statistics remain in the
supplement. No ordinal classes or favorable replacement statistics were added.
Existing CASPOTS scores are preserved; their optimizer was not rerun for this
presentation/formal-audit revision.

## Figures
Figure 1: new biology/readout-first workflow.
Figure 2: new combined GIM biological abstraction and generated A/B/C results.
Figures 3-4: both full Petri nets retained in Appendix B.
Supplementary Figures S1-S2: synthetic benchmark and HPN plot retained.
R2 names avoid collisions with previous uploads.

## Tests/reproducibility
New independent raw-edge weak-target/game implementation, exact trace checker,
supplied-relation checker and deletion certificates; 32 ordered pair records;
three hierarchy witnesses; expanded exhaustive audit; direct tau-free mCRL2
simulation checks. Notebook includes new executable cells and foregrounds GIM.
R1 remains immutable. Inline bibliographies are reordered by first citation.
Upload archives are flat and clean-built without BibTeX or cached auxiliary files.

## Claims/limitations
Prior biological evidence is distinct from encoded hypotheses and computed
relations. No organism-level equivalence, experimental confirmation, prognosis,
or mechanistic discovery is claimed. Small curated nets and inconclusive HPN
data remain limitations, not issues solved by additional software tests.
