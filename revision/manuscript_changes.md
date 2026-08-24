# Manuscript changes for JBCB-1505

## Abstract

- Rebalanced the abstract toward the biological model-comparison problem.
- Added the executed GIM result: fixed PN-GDDA `0.9976`, weak bisimulation at A/B, non-comparability at C, and `d6=0.353`.
- Labeled the six constructed cases as software verification and HPN-DREAM as exploratory.
- Reduced the abstract to 178 words, below the JBCB 200-word limit.

## Introduction

- Introduced GIM as the motivating biological problem rather than a late illustration.
- Defined the observational interface as a biological hypothesis.
- Distinguished structural, trace, local labeled, and branching-time questions.
- Introduced the four evidence layers and narrowed all organism-level claims.

## Formal framework

- Preserved the definitions, simulation orientation, fixed-point algorithm, correctness theorem, termination argument, hierarchy, and counterexamples.
- Retained “graded” only as an implication-aware reporting priority, not a scalar or algebraic order.

## Computational implementation and verification

- Renamed and reframed the six-pair benchmark as construction-level software/formal verification.
- Redesigned its vector figure for normal manuscript-scale reading.
- Preserved mCRL2, Holmes, exhaustive simulation-game, and scaling results.
- Clarified that PN-GDDA and behavioral relations answer complementary questions.

## Biological applications

- Reorganized the section so GIM appears first and follows question, independent biology, structural result, behavioral results, interpretation, and hypothesis.
- Added biological rationale Table 2 with verified literature support.
- Added three fixed interfaces on unchanged GIM structures:
  - A: coarse functional/process observations.
  - B: damage, ATM/ATR, and repair distinctions with terminal fate collapsed.
  - C: apoptosis, SMR induction, and the encoded plant terminal outcome separated.
- Added result Table 3 and central vector Fig. 3.
- Retained public GINsim models as ingestion/execution controls.
- Rewrote HPN as exploratory, removed the ordinal class analysis, and preserved simulation direction.
- Kept RCD as a limited secondary directional example; DCE, SPS, and AID are supporting cases.

## Discussion

- Added a direct GIM demonstration of structural/behavioral complementarity.
- Explained why `Sigma` and update semantics are part of the biological comparison contract.
- Added Table 7 separating formal correctness, software verification, executable-model support, and biological interpretation.
- Expanded limitations concerning kinetics, concentrations, stochasticity, tissue context, interface selection, update semantics, empirical sample size, and lack of independent calibration for curated nets.

## Conclusion

- Replaced method-superiority language with a restrained complementarity claim.
- Stated the actual A/B-to-C GIM transition and its model-level interpretation.
- Preserved the explicit exclusion of prognosis, cell-line specificity, mechanistic identity, and organism-level equivalence.

## Figures and appendix

- Replaced the compressed GIM nets in the main narrative with a biological abstraction, control-flow view, and interface-result panel.
- Retained the complete animal/human and Arabidopsis Petri nets at full width in Appendix A.
- Replaced the HPN ordinal class plot with a nominal, direction-preserving display.
- Kept all main figures vector-based.

## Reproducibility

- Added `src/gim_interface_analysis.py` and deterministic GIM CSV/TeX outputs.
- Corrected `src/hpn_dream_validation.py` to remove the arbitrary ordinal class scale.
- Added regression tests for GIM definitions/results/output generation, direction preservation, obsolete-field absence, figure dependencies, and manuscript-result consistency.
- Updated and executed `notebooks/metodologia_multiescala.ipynb` end to end.
- Updated `README.md`, `REPRODUCIBILITY.md`, and Make targets.
- Re-ran mCRL2 202607.0, all 46 tests, figures, and manuscript compilation.
