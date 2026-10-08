# Formal Direction Audit: R2

Convention: left <=_w right means **right simulates left**.
Production weak_simulates(left,right), the new independent game, the manuscript
definition, and machine-readable fields use this same orientation.

The statement inventory covers current R2 source/captions, source modules,
result CSV/JSON/TeX files, tests, README, reproducibility guide and notebook
source plus rendered textual outputs. Historical journal manuscripts and the
immutable R1 archive are not rewritten. Older scripts/functions retain compatible
names; their parameter roles are documented and checked against primitive
predicates. An occurrence inventory is a navigation aid, not a proof that
arbitrary prose was automatically verified.

## Audited locations and roles

| Statement/location | Mathematical relation | Expected orientation | Computed/independent check | Status and action |
|---|---|---|---|---|
| Definition 4, Section 3.3 | L1 <= L2 | right simulates left | raw-edge game agrees with production | Retained, clarified |
| Example 1, Appendix A | early <= late only | candidate in reference | exact relation certificate and mCRL2 on tau-free inputs | Retained; expanded proof |
| Proposition 2 and Table 5 | strong => weak => mutual => equal traces | each converse has a distinct witness | three independently checked constructions | Retained; witness roles explicit |
| Synthetic Table S1 and Figure S1 | added branch: reference <= candidate; early choice: candidate <= reference | left=reference, right=candidate | six class and primitive-predicate checks | No reclassification |
| GIM Table 2/Figure 2 | A/B both directions; C neither | left=animal, right=plant | regenerated interfaces and raw-edge oracle | No change |
| Curated Table 3 and RCD paragraph | plant <= animal only | right=plant, left=animal in audit | source compare_module and independent game | No change |
| HPN Section 6/Figure S2 | explicit left/right Booleans, nominal categories | alphabetical cell-pair order is preserved | all 18 asynchronous/synchronous pairs independently checked | No ordinal conversion |
| concurrent_biomodels.compare_module | plant_le_animal = weak_simulates(plant,animal) | animal is defender | unchanged outputs and regression tests | Correct |
| method_benchmark.classify_pair | reference_simulated_by_candidate | candidate is defender | swapped-order Example 1 test | Correct |
| HPN validation_rows | left_simulated_by_right | right is defender | direction-preserving tests and pair audit | Correct |
| README / REPRODUCIBILITY / notebook | same conditional GIM, RCD and HPN meanings | no inversion in public narrative | executed outputs match unchanged deterministic result tables | R2 context updated |

No mathematical or directional correction was discovered. The new ambiguity
removed is quantifier scope in Example 1, not a reversed result. The statement
that weak simulation implies trace inclusion is never used as its converse.

## Per-pair computed directions

All rows below have agreement on strong/weak bisimilarity and both simulations
with the independently implemented raw-edge game. For curated/GIM rows,
left=animal and right=plant. HPN row IDs give left/right cell order.

| Case | Left simulated by right | Right simulated by left | Weak bisimilar | Exact traces equal | Independent agreement |
|---|---|---|---|---|---|
| synthetic_identity | True | True | True | True | True |
| synthetic_silent refinement | True | True | True | True | True |
| synthetic_label mismatch | False | False | False | False | True |
| synthetic_label order swap | False | False | False | False | True |
| synthetic_added branch | True | False | False | False | True |
| synthetic_trace-equivalent branching | False | True | False | True | True |
| GIM_A | True | True | True | True | True |
| GIM_B | True | True | True | True | True |
| GIM_C | False | False | False | False | True |
| GIM | True | True | True | True | True |
| DCE | True | True | True | True | True |
| SPS | True | True | True | True | True |
| RCD | False | True | False | False | True |
| AID | False | False | False | False | True |
| HPN_asynchronous_mTORi_BT20_BT549 | False | True | False | False | True |
| HPN_asynchronous_mTORi_BT20_MCF7 | False | False | False | False | True |
| HPN_asynchronous_mTORi_BT549_MCF7 | True | False | False | False | True |
| HPN_asynchronous_IGF1+mTORi_BT20_BT549 | False | True | False | False | True |
| HPN_asynchronous_IGF1+mTORi_BT20_MCF7 | False | False | False | False | True |
| HPN_asynchronous_IGF1+mTORi_BT549_MCF7 | False | False | False | False | True |
| HPN_asynchronous_4EBP1+mTORi_BT20_BT549 | False | True | False | False | True |
| HPN_asynchronous_4EBP1+mTORi_BT20_MCF7 | True | False | False | False | True |
| HPN_asynchronous_4EBP1+mTORi_BT549_MCF7 | True | False | False | False | True |
| HPN_synchronous_mTORi_BT20_BT549 | False | True | False | False | True |
| HPN_synchronous_mTORi_BT20_MCF7 | False | False | False | False | True |
| HPN_synchronous_mTORi_BT549_MCF7 | True | False | False | False | True |
| HPN_synchronous_IGF1+mTORi_BT20_BT549 | False | False | False | False | True |
| HPN_synchronous_IGF1+mTORi_BT20_MCF7 | False | False | False | False | True |
| HPN_synchronous_IGF1+mTORi_BT549_MCF7 | False | False | False | False | True |
| HPN_synchronous_4EBP1+mTORi_BT20_BT549 | False | True | False | False | True |
| HPN_synchronous_4EBP1+mTORi_BT20_MCF7 | False | False | False | False | True |
| HPN_synchronous_4EBP1+mTORi_BT549_MCF7 | True | False | False | False | True |

Inventory: 1324 matched source/output lines in direction_statement_inventory.csv.
