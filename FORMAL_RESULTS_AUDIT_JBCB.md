# Formal Results Audit for JBCB

Audit date: 2026-08-13. Scientific source: `paper/jbcb/main_jbcb.tex`.
Implementation source: `src/concurrent_biomodels.py`. `VERIFIED` means that the
statement, implementation, and targeted regression agree. Proofs drafted or
edited with Codex remain `NEEDS_AUTHOR_REVIEW` until the author accepts the
argument as his own; computational tests are not substitutes for proofs.

| result | assumptions | proof checked | code consistency | terminology | status |
|---|---|---|---|---|---|
| Orientation of `L1 <=w L2` | finite LTSs over the declared interface; the right system matches the left | definition inspected | `weak_simulates(L1,L2)` and orientation regression agree | consistently "right simulates left" | VERIFIED |
| Silent closure and `W_tau=Cl_tau` | zero or more internal moves; observable weak moves are `tau* a tau*` | definition inspected | direct closure/weak-step test passes | `tau` is internal, never an observable wildcard | VERIFIED |
| Exclusive classifier | priority strong, weak, mutual, two directed classes, non-comparable | exhaustive Boolean split checked | exclusive-output regression passes | reporting class, not a new equivalence | NEEDS_AUTHOR_REVIEW |
| Greatest-fixed-point relation deletion | finite state product; immediate in-place deletions; final complete no-deletion pass | monotonicity, preservation of `nu Phi`, terminal fixed point, and maximality checked | production loops implement the stated deletion rule | proof distinguishes theorem from software evidence | NEEDS_AUTHOR_REVIEW |
| Strong/weak/simulation hierarchy | definitions in the manuscript; common interface | implication steps and path induction checked | strong-to-weak and both simulation directions tested | exact weak language, not depth-limited distance | NEEDS_AUTHOR_REVIEW |
| Mutual simulation need not be bisimulation | `a.(b+c)+a.b` versus `a.(b+c)` | successor argument checked | new mutual-simulation regression passes | no equivalence claim is attached to mutual simulation | VERIFIED |
| Exact versus truncated traces | finite weak language versus `L_<=k` | definitions checked | a pair equal at depth 2 and unequal at depth 6 is tested | `d_k=0` is never called exact equality | VERIFIED |
| Controlled silent edge refinement | one selected observable edge; fresh intermediate state with no other incident behavior | explicit relation and strong counterargument checked | weak-yes/strong-no test passes | not generalized to arbitrary Petri-net refinement | NEEDS_AUTHOR_REVIEW |
| Label-blind limitation | comparator depends only on unlabeled structure and is relabeling invariant | two-state counterexample checked | PN-GDDA self/mismatch score and formal relations tested | presented as a scope distinction, not a PN-GDDA defect | NEEDS_AUTHOR_REVIEW |
| Equal traces, different branching | acyclic early/late choice systems | exact language and direction checked | Python and mCRL2 trace/bisimulation controls agree | early is contained in late, not conversely | NEEDS_AUTHOR_REVIEW |
| Resource bound | explicit state enumeration and pair deletion | bound checked without asserting tight runtime complexity | scaling metadata gives 129 x 145 states and 18,705 pairs | observed scaling, no genome-scale claim | VERIFIED |

## In-place deletion check

For each monotone operator, the proof preserves `G = nu Phi` inside the current
relation: a member of `G` cannot fail a transfer test against a superset of `G`.
At termination, retained pairs pass against the unchanged final relation. A pair
deleted from an earlier superset cannot re-enter `Phi(R*)` by monotonicity.
Therefore the terminal relation is a fixed point containing `G`; greatestness
gives equality. This reasoning matches the immediate-deletion implementation.

## Regression coverage

`tests/test_formal_properties.py` now explicitly checks all ten semantic cases
requested in the revision instructions: strong implies weak; weak bisimulation
implies both simulations; mutual simulation without bisimulation; controlled
silent refinement; trace-equal branching; orientation; label mismatch;
classifier exclusivity; exact versus truncated traces; and `tau` closure.

No statement needs correction or deletion. The six proof-bearing items marked
`NEEDS_AUTHOR_REVIEW` must receive human intellectual review before submission.
