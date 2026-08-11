# AI use log

- Review date: 2026-08-11
- Tool: OpenAI Codex
- Role: editorial, programming, formatting and reproducibility assistance under
  human responsibility
- Author sign-off at handoff: pending

## Tasks performed

| Task | Codex activity | Scientific boundary |
|---|---|---|
| Repository audit | Located manuscript, code, data, tests, figures and build paths; preserved baseline logs. | No scientific output changed. |
| JMCS migration | Applied the official `ISRP.cls`, reorganized sections and adapted citations, theorem environments and declarations. | The official class and logo were not modified. |
| Formalization | Converted the implemented semantics into definitions, fixed-point operators, a reporting classifier and proof drafts. | Relations are standard; no claim of a new bisimulation algorithm was added. |
| Software checks | Added regression tests for hierarchy, silent refinement, branching, orientation, relabelling, classifier exclusivity and deterministic benchmark output. | Tests support the implementation; they are not presented as mathematical proofs. |
| Reproducibility | Ran tests, public-model checks, HPN-DREAM validation, the simulation oracle, PN-GDDA/Holmes checks, figure generation and the notebook. | Data, thresholds, negative results and figures were not selected or altered to improve conclusions. |
| References | Checked DOI-bearing records and non-DOI publisher/institutional sources; prepared the alphabetical JMCS list. | No unverified reference was introduced. |
| Language | Made targeted edits for clarity, scope discipline and LaTeX correctness. | No mass generative rewrite or AI-generated figure was used. |
| Delivery | Built and independently compiled the clean JMCS source package. | No submission or remote push was performed. |

## Files affected

- `paper/jmcs/main.tex`, `paper/jmcs/references.bib`, and
  `paper/jmcs/references_jmcs.tex`
- `tests/test_formal_properties.py` and the mCRL2 availability guard in
  `tests/test_hpn_dream_validation.py`
- `Makefile`, `README.md`, `REPRODUCIBILITY.md`, `.gitignore`, and
  `scripts/build_jmcs_package.py`
- `JMCS_BASELINE_AUDIT.md`, `REFERENCE_AUDIT.md`, `CLAIM_AUDIT.md`,
  `COVER_LETTER_JMCS.md`, and `JMCS_REVISION_REPORT.md`
- Generated final PDF, executed notebook output, audit logs and submission bundle

## Required human review

| Item | Human verification status |
|---|---|
| Theorem 2.9, greatest-fixed-point proof | PENDING (`AUTHOR_PROOF_REVIEW_REQUIRED`) |
| Proposition 2.6, exclusive reporting | PENDING (`AUTHOR_PROOF_REVIEW_REQUIRED`) |
| Proposition 2.11, relation hierarchy | PENDING (`AUTHOR_PROOF_REVIEW_REQUIRED`) |
| Proposition 2.12, controlled silent refinement | PENDING (`AUTHOR_PROOF_REVIEW_REQUIRED`) |
| Proposition 2.13, label-blind limitation | PENDING (`AUTHOR_PROOF_REVIEW_REQUIRED`) |
| Example 2.14, trace/branching orientation | PENDING (`AUTHOR_PROOF_REVIEW_REQUIRED`) |
| Author identity, affiliation, funding, conflicts and ethics statements | PENDING AUTHOR CONFIRMATION |
| `Declaration of AI Use` wording and scope | PENDING AUTHOR APPROVAL |
| Final English voice and cover-letter exclusivity statement | PENDING AUTHOR APPROVAL |

No mathematical proof in the JMCS revision has been recorded by Codex as
verified by the author. Computational checks passed, but they do not replace
that intellectual review. The manuscript must not be submitted until the author
has reviewed the items above and can truthfully accept the declaration.
