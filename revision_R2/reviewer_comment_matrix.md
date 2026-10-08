# Reviewer-Comment Matrix: Second Revision

Headings paraphrase the concerns supplied in the second-round prompt.
No standalone full verbatim reviewer report was supplied with this request.

| ID | Reviewer concern | Agree/disagree | Action | Manuscript location | Code/test | Response section | Status |
|---|---|---|---|---|---|---|---|
| R2.1 | Alleged two-way simulation in Example 1 | Respectfully disagree on direction; agree exposition needed clarity | Witness, failed successors, independent audit | Appendix A, Example 1; Section 3 | formal_revision_audit.py; test_example1_direction_and_explicit_witness | R2.1 | Original direction retained after audit |
| R2.2 | Hierarchy converse witnesses | Agree need clarity | Three-witness table and middle-witness proof | Appendix A, Proposition 2, Table 5 | test_three_strictness_witnesses; mcrl2_hierarchy_R2.json | R2.2 | Clarification and independent audit |
| R2.3 | Audit all directional results | Agree | Primitive predicates, generated direction table, occurrence inventory | Sections 3-6; Tables 2-3; Supplement S1/S4 | direction_audit_R2.json; synthetic, GIM, RCD, HPN tests | R2.3 | Fully addressed within scope |
| R2.4 | Fixed-point correctness | Agree theorem is sound after audit | Retain proof; independent weak-target implementation | Appendix A, Theorem 1; Section 3 | independent game and exhaustive hierarchy checks | R2.4 | Clarification and independent audit |
| R2.5 | Formal-methods-centric title | Agree | Biology/readout title | Title, metadata, running head | test_R2_positioning | R2.5 | Substantial restructuring |
| R2.6 | Abstract overweights software and HPN | Agree | Rewrite; GIM dominates; remove software counts and p=0.25 | Abstract | abstract checker and positioning test | R2.6 | Substantial restructuring |
| R2.7 | Intro and contribution not biology-first | Agree | Complete intro rewrite; biological models before math | Sections 1-3 | section ordering test | R2.7 | Substantial restructuring |
| R2.8 | GIM too late in results | Agree | GIM first results, with five focused subsections | Section 4, Figure 2, Table 2 | gim_interface_analysis; generated figure | R2.8 | Substantial restructuring |
| R2.9 | Excess prominence of software validation | Agree | Compact check/method/outcome table in main text; detailed controls and scaling in supplement; proofs in appendix | Section 7, Table 4; Appendix A; Supplement S1/S2/S4 | verified outcome counts and clean compilation | R2.9 | Substantial restructuring |
| R2.10 | HPN inconclusive and overemphasized | Agree | Secondary exploratory section; full negative results retained | Section 6; Supplement S3/Figure S2 | HPN anti-leakage, direction and permutation tests | R2.10 | Interpretation addressed; evidence still limited |
| R2.11 | Do not oversell deliberately encoded GIM distinctions | Agree | Prior knowledge vs computed boundary vs unvalidated implication | Sections 2, 4.4-4.5, 8.3, conclusion | unchanged nets/interfaces; claim audit | R2.11 | Interpretation addressed; no experimental validation claimed |
| R2.12 | Make figures biological and readout-centered | Agree | New workflow and central figure; nets retained | Figures 1-4; Supplement S1-S2 | make_revision_R2_figures.py; PDF visual QA | R2.12 | Substantial restructuring |
| R2.13 | Discussion/conclusion and jargon need repositioning | Agree | Three biological/computational questions; GIM-led conclusion | Sections 8-9 | narrative consistency checks | R2.13 | Substantial restructuring |
