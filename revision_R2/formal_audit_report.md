# Formal Audit Report: JBCB-1505 R2

## Scope and baseline

The supplied JBCB-1505.zip is authoritative. Its nine files are preserved in
original_R1/ and identified by baseline_sha256.json. The R1 article contains
an inline bibliography. No other journal manuscript was substituted.
The second-round prompt supplies a description of reviewer concerns, not a
separately attached complete verbatim report. Response headings therefore
summarize those concerns without fabricating quotations.

## Manual audit

| Claim | Derivation and mathematical expectation | Computational check | Action |
|---|---|---|---|
| Definition 4 | For every related pair and left transition, a right weak successor must exist AND remain related. Right simulates left. | Production, original game, new independent weak-target game, direct relation check | Retain; make quantifiers explicit |
| Example 1 | Exact languages are {epsilon,a,ab,ac}. Early <= late, not late <= early. No weak bisimulation. | Complete acyclic enumeration; finite subset product; production; two games; mCRL2 on tau-free inputs | Add five-pair witness and two failed-successor cases |
| Proposition 1 | Strong/weak priority followed by four Boolean combinations is disjoint and exhaustive. | Existing classifier-priority tests; six constructed classes | Retain |
| Theorem 1 monotonicity | Enlarging R preserves every existential witness. | Independent simultaneous-round game contrasted with in-place production | Retain proof |
| Theorem 1 invariant | nu(Phi) is a subset of every current R; a greatest-fixed-point pair cannot be deleted. | All independently checked predicates agree | Retain |
| Theorem 1 terminal equality | Final no-deletion pass gives R subset Phi(R); a removed pair fails for the final, smaller relation by monotonicity. Therefore Phi(R) subset R. | No discrepancies over finite universe | Retain |
| Theorem 1 termination | At most n1*n2 deletions and n1*n2+1 passes, including final empty-change pass. | Algorithm inspection; finite tests | Retain; do not infer a tight runtime bound |
| Proposition 2 forward hierarchy | Direct targets are weak targets; a bisimulation and its inverse are simulations; induction along concrete paths gives trace inclusion. | Strong=>weak, weak=>both simulations, simulation=>exact inclusion over 67,600 pairs | Retain |
| Converse weak=>strong | a.0 versus a.tau.0 is weak but not strong. | Production, independent game, mCRL2 | Retain; explicit table |
| Converse mutual=>weak bisimulation | a.(b+c)+a.b versus a.(b+c): both simulations, but the extra b-only successor cannot match c in a bisimulation. | Production, independent game, mCRL2 | Retain; distinguish from Example 1 |
| Converse equal traces=>mutual | Late/early pair has equal traces and only early<=late. | Exact language and simulation audits | Retain |
| Proposition 3 silent refinement | Identity pairs plus (q,r) witness a.(r)-tau-q subdivision; r matches via q and its tau matches stuttering. Additional stated condition excludes a strong match. | Controlled refinement regression; general relation argument | Retain; not arbitrary refinement |
| Proposition 4 label blindness | Relabel a single edge from a to b; identical unlabeled input, different language and no simulation. | Label-renaming regression | Retain; not a defect in PN-GDDA |

The reviewer-described assertion that both directions hold for Example 1 is
not compatible with Definition 4. No mathematical or directional result was
changed to agree with it. The corrected issue is expositional ambiguity.
The fixed-point theorem remains intact, relocated to Appendix A.

The witness early-to-late is
{(e0,l0),(eb,l1),(ec,l1),(eb',lb),(ec',lc)}.
In the reverse game, (l1,eb) loses on c and (l1,ec) loses on b.
Only after these failures does (l0,e0) lose all a-replies.
The JSON certificate records the rounds and dependencies.

## Independent computation

The R2 oracle reads raw edges, state counts and initial indices only. It does
not reuse production adjacency, silent closure, weak_step or relation routines.
It grows the least losing set in simultaneous rounds. A separate transparent
checker verifies supplied relations. Exact traces use epsilon-NFA subset-product
exploration with all original states accepting, with no depth limit. Complete
finite enumeration is used only after checking reachable acyclicity.

Existing production algorithms were not changed. The original simulation oracle
shares the production weak-target helpers; the new R2 oracle removes that shared
dependency. Agreement with the old oracle is complementary, not claimed as
full implementation independence of its weak-target construction.

mCRL2 202607.0 was downloaded from its official release; arm64 DMG SHA-256:
e584919454b0d774800eff964f19dad2e0a0eac91e571f788aae4ab1a87a207f.
Its documented strong simulation preorder is used only for the tau-free
Example 1 and middle witness, where strong and weak simulation coincide.
No general weak simulation capability is attributed to mCRL2.
Official documentation:
https://www.mcrl2.org/web/user_manual/tools/release/ltscompare.html

## Regenerated outcomes

- 32 ordered model pairs: six synthetic, three GIM interfaces, five curated
  modules, and 18 asynchronous/synchronous HPN pairs.
- All production and independent strong/weak bisimulation and direction
  predicates agree for those pairs and the three strictness witnesses.
- All six predeclared synthetic classes remain unchanged.
- GIM PN-GDDA = 0.9975845917160132 for all interfaces; A/B weakly bisimilar
  with both simulation directions; C has neither direction and d6 = 6/17.
- RCD: plant <= animal is true; animal <= plant is false.
- HPN asynchronous: three left-in-right, three right-in-left, three neither.
  Synchronous stress retains seven of nine nominal classes. No ordinal coding.
- 67,600 ordered pairs over 260 named one-/two-state LTSs on {a,tau}:
  no discrepancies or hierarchy failures; simulation reflexive and transitive.
  There are 41,080 weakly bisimilar pairs and 4,848 mutually simulated but
  non-bisimilar pairs. No one-way/equal-trace pair exists in this limited universe.
- Original deterministic scientific outputs are unchanged by regeneration;
  runtime values are hardware-dependent and excluded from byte comparison.

The exact values and per-pair directions are in the generated JSON/CSV files,
not inferred from these prose claims. The tests guard primitive predicates.

## Biological interpretation audit

The paper now distinguishes prior DDR knowledge, structural similarity,
model-level branching correspondence, and unvalidated experimental consequences.
The boundary is between B and C within three declared interfaces, not a globally
minimal or unique observational resolution. The terminal plant transition is
combined differentiation/endoreduplication, not two distinct choices.
HPN remains exploratory and inconclusive; no new p-value search was performed.
No models, interfaces, empirical scores, or biological conclusions were altered
merely to increase apparent acceptance prospects.
