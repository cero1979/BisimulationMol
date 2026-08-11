# Claim audit

Audit date: 2026-08-11. `PROVED` means that a derivation is present in the
manuscript; it does not mean that the author has signed off on the Codex-assisted
proof draft. Human proof review remains mandatory in `AI_USE_LOG.md`.

| Claim ID | Manuscript claim | Source | Mathematical proof | Code/test | External source | Status |
|---|---|---|---|---|---|---|
| C01 | The graded classifier returns exactly one priority class. | `paper/jmcs/main.tex`, Definition/Proposition 2.6-2.7 | Exhaustive Boolean case split | `test_classifier_returns_one_exclusive_priority_class` | Not needed | PROVED |
| C02 | Relation deletion terminates on finite LTSs and returns the greatest fixed point for simulation and bisimulation. | Theorem 2.9 | Monotonicity, finite deletion, invariant and fixed-point argument | Production engine plus formal-property regressions | Standard fixed-point theory | PROVED |
| C03 | Strong bisimilarity implies weak bisimilarity, which implies mutual weak simulation; mutual simulation implies exact finite weak-trace equality. | Proposition 2.11 | Transfer-clause inclusions and path induction | `test_strong_bisimilarity_implies_weak_and_mutual_simulation` | Milner; Sangiorgi | PROVED |
| C04 | The benchmark's observable-then-silent edge subdivision preserves weak but, under stated conditions, not strong bisimilarity. | Proposition 2.12 | Explicit relation and strong counterargument | `test_controlled_silent_refinement_is_weak_but_not_strong` | Not needed | PROVED |
| C05 | A label-blind relabelling-invariant comparator cannot characterize labelled trace, simulation or bisimulation semantics. | Proposition 2.13 | Two-state relabelling counterexample | `test_label_renaming_preserves_unlabelled_topology_not_behaviour` | PN-GDDA scope: Szawulak and Formanowicz | PROVED |
| C06 | The two branching examples have exact language `{epsilon,a,ab,ac}`, are not weakly bisimilar, and satisfy only candidate/early <= reference/late. | Example 2.14 | Explicit successor analysis | `test_equal_exact_traces_do_not_hide_branching_direction`; orientation test | mCRL2 weak-trace result | PROVED |
| C07 | Synthetic binary decisions are 6/6 weak bisimulation, 5/6 truncated trace, 4/6 LTS-GDA, 3/6 structural profile and 2/6 PN-GDDA. | `results/baseline_accuracy.csv` | Not applicable | Deterministic benchmark tests | mCRL2 for formal/trace controls | COMPUTATIONALLY_VERIFIED |
| C08 | The independent game agrees on all 67,600 ordered pairs among 260 one-/two-state LTSs over `{a,tau}`. | `results/simulation_oracle_exhaustive.csv` | Finite-universe enumeration only | `test_all_one_and_two_state_lts_pairs_agree` | Independent implementation | COMPUTATIONALLY_VERIFIED |
| C09 | Python and mCRL2 agree on all 42 reported strong/weak decisions. | Synthetic, public and HPN validation CSVs | Not applicable | 12 synthetic + 12 public + 18 HPN decisions | mCRL2 202607.0 `ltscompare` | EXTERNALLY_VERIFIED |
| C10 | The published/Holmes catalog has 151 graphlets and 592 slots. | `results/pn_gdda_catalog_validation.json` | Enumeration by size 2, 6, 23, 120 | PN-GDDA catalog tests | Holmes 1.1.1 and 2.0.1.2 artifacts; published PN-GDDA paper | EXTERNALLY_VERIFIED |
| C11 | The type/direction-preserving automorphism sensitivity catalog has 576 distinct orbits. | `results/pn_gdda_catalog_validation.json` | Automorphism partition computation | `test_automorphism_sensitivity_catalog_has_576_orbits` | Not a replacement for the published catalog | COMPUTATIONALLY_VERIFIED |
| C12 | Independent Python PN-GDDA matches Holmes to 12 decimals. | `results/holmes_pn_gdda_external_validation.json` | Not applicable | Catalog and score regression tests | Hash-verified Holmes 1.1.1 JAR | EXTERNALLY_VERIFIED |
| C13 | Public models have 826/3,413 and 17/26 reachable states/edges. | `results/public_models.csv` | Reachability enumeration | Public-model tests | Hash-verified GINsim SBML-qual/GINML files | COMPUTATIONALLY_VERIFIED |
| C14 | HPN family sizes are 72, 191 and 21; structure-only medoids are rows 24, 137 and 9. | `results/hpn_dream_medoids.csv` | Not applicable | Stability and anti-leakage tests | Hash-verified CASPOTS commit `95e3c74` | COMPUTATIONALLY_VERIFIED |
| C15 | Nine HPN pair-condition comparisons contain six one-way and three non-comparable classes. | `results/hpn_dream_formal_data_validation.csv` | Not applicable | HPN formal validation tests | mCRL2 cross-check | EXTERNALLY_VERIFIED |
| C16 | LTS-GDA/held-out distance has rho=0.669 and one-sided exact p=0.097. | `results/hpn_dream_concordance.json` | Exact 216-permutation design | Concordance-null test | Held-out HPN-DREAM responses | EMPIRICAL_ONLY |
| C17 | Native-cell specificity is not established; exact paired sign p=0.25. | `results/hpn_dream_caspots_summary.json` | Exact 8-sign permutation | Repeated deterministic CASPOTS scores | Held-out HPN-DREAM responses | EMPIRICAL_ONLY |
| C18 | Synchronous stress preserves seven of nine HPN classes. | `results/hpn_dream_semantic_sensitivity.csv` | Not applicable | Semantic-sensitivity regression | Not needed | COMPUTATIONALLY_VERIFIED |
| C19 | The largest scaling pair has 129 versus 145 states and 18,705 candidate pairs; runtime is about 0.6 s on the reported machine. | `results/scalability_structure.csv`; `results/scalability_runtime.csv` | Candidate product 129 x 145 | Scaling metadata test | Hardware-dependent timing | CONDITIONAL |
| C20 | Curated GIM/DCE/SPS are weakly bisimilar, RCD is one-way, and AID is non-comparable at the declared interfaces. | `results/phase6_comparisons.csv` | Model-specific computation | Case-study regression | Curated definitions only | CONDITIONAL |
| C21 | Direct native PN-GDDA scores remain 0.9904-1.0000 while behavioural classes vary. | `results/pn_gdda_native_modules.csv` | Not applicable | Native-module sensitivity tests | Published/Holmes catalog | COMPUTATIONALLY_VERIFIED |
| C22 | The applications do not establish predictive performance, cell specificity or organism-level equivalence. | Scope statements and negative empirical tests | Not a positive claim | C16-C20 evidence boundaries | Source-model provenance | CONDITIONAL |

No claim retained in the final manuscript is classified `UNSUPPORTED`.
