# Final scientific/code review

## Historical review of the initial R3

The review below predates the sustained-trace counterexample. The baseline
correction of 2026-09-23 has separate tests and artifact verification; it is
not represented as an independently reviewed scientific revision.

An independent fresh-context reviewer inspected the R3 executors, provenance,
trace limits, all-defender certificate, conditioned/global scope and biological
claims. No critical scientific or computational error was reported in that
bounded review. Small direct diagnostics confirmed the original 28-node local
results and the rejection of a certificate missing a defender reply.

One metadata-binding issue was identified: the verifier checked the losing
game but not that its orientation matched the reported failed relation.
Although the stored biological result was correctly labeled, this was treated
as important for the reusable verification contract. A new regression test
first failed on four altered results (swapped direction, a true failure flag,
wrong game type and unknown relation), then passed after binding relation,
orientation and the false flag. No scientific result changed.

The reviewer accepted the approved endpoint-level Pattern B interpretation,
not the stronger equal-global-trace/different-branching demonstration.

The coordinator separately verified full tests, regeneration, notebook, PDF
layout and archive compilation. The independent reviewer did not rerun the
large global graphs or the costly mCRL2 checks. Neither party claims that
local timestamps externally prove preregistration or that software verification
establishes experimental validity. Candidate 2 was not evaluated in that
initial review; a later feasibility probe found unequal traces.

No second review round was used; the correction is supported by its failing
then passing regression and the final full-suite run.

## Baseline correction, 2026-09-23

This follow-up was self-reviewed locally; no fresh independent reviewer was
available. The global sustained inequality follows from a concrete word, not
from a timeout. Its positive path is checked against the original rules;
regenerated-graph mCRL2 checks agree. The reverse inclusion remains unknown.
The 19 accepted mathematical environments are unchanged, as is the exact
shared-state sustained equality. The current figure, paper, supplement,
response and executed notebook consistently separate these scopes.

Three new regressions failed on the old state and passed after correction.
The full suite passed 90 tests and the notebook executed 28 code cells without
errors. Clean-build and layout reports accompany the updated artifacts. The
portable archive excludes its own archive-hash report to avoid embedding an
inevitably stale self-reference; a regression first failed and then passed.
