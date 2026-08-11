# Cover letter to JMCS

> Draft for author approval. Before sending, confirm that the manuscript is not
> under consideration elsewhere and that all declarations are accurate.

11 August 2026

Editor-in-Chief
Journal of Mathematics and Computer Science

Dear Editor-in-Chief,

I submit the manuscript **“A graded behavioural comparison framework for
labelled Petri nets and qualitative network models”** for consideration in the
*Journal of Mathematics and Computer Science*.

The paper addresses a formal model-comparison problem: given two finite
executable labelled models and an observational interface, determine the
strongest supported relation between their reachable transition systems without
conflating structural similarity, trace agreement, branching-time equivalence
and directional containment. It defines an exclusive reporting classifier over
strong and weak bisimilarity and weak simulation, proves correctness of the
implemented greatest-fixed-point deletion procedure, and gives controlled
results and counterexamples separating silent refinement, labels, traces and
branching.

The implementation is checked against construction-level cases, mCRL2 and an
independently coded simulation game. The latter agrees on all 67,600 ordered
comparisons in the explicitly bounded universe of one- and two-state LTSs used
for the audit. Public GINsim models, HPN-DREAM/CASPOTS families and curated Petri
nets are included as applications of the formal framework. Their empirical
limitations and dependence on update semantics and observational interfaces are
reported explicitly; the manuscript makes no claim of prognostic performance or
organism-level equivalence.

The complete code, hash-verified public inputs, tests, executed notebook and
generated results are available at
<https://github.com/cero1979/BisimulationMol>. The manuscript includes a
declaration of AI use in accordance with the journal policy. No human
participants, human samples or live animals were involved.

I confirm, subject to final author verification before submission, that this is
original work, that it is not under consideration by another journal, and that I
take responsibility for the manuscript and its supporting artifacts.

Sincerely,

Carlos Ramirez Ovalle

Department of Natural Sciences and Mathematics

Pontificia Universidad Javeriana Cali

Cali, Colombia

carlosovalle@javerianacali.edu.co
