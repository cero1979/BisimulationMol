# Cover Letter - Journal of Bioinformatics and Computational Biology

**Author check before use:** confirm that the manuscript is not under
consideration elsewhere and that the affiliation, funding, conflict, and contact
details remain current.

13 August 2026

Editor-in-Chief
*Journal of Bioinformatics and Computational Biology*

Dear Editor,

Please consider the manuscript, **"A formal and reproducible framework for
auditing observable behavior in qualitative biological network models,"** for
publication as a Research Paper in the *Journal of Bioinformatics and
Computational Biology*.

Qualitative regulatory and signaling models are frequently compared through
network structure, although similar topology does not ensure preservation of
event order, hidden steps, branching, or directional behavioral containment.
The manuscript addresses this computational biology problem by mapping
executable Petri-net and logical models to reachable labeled transition systems
under a declared observational interface. It then reports the strongest
supported relation among strong or weak bisimilarity, mutual or one-way weak
simulation, and non-comparability, while retaining structural and trace scores
as separate diagnostics.

The main contributions are:

1. a formal model-audit workflow with an implication-aware classifier and
   explicit interface and update-semantics assumptions;
2. a greatest-fixed-point correctness theorem, relation hierarchy, controlled
   silent-refinement result, and counterexamples separating topology, traces,
   and branching;
3. independent computational validation through six construction-level cases,
   mCRL2, and an attacker-defender implementation agreeing on all 67,600
   ordered comparisons in the declared small-LTS universe; and
4. applications to externally authored public GINsim models and public
   HPN-DREAM/CASPOTS model families with held-out perturbation-response data,
   complemented by an interface-dependence case study on curated Petri nets.

The empirical results are reported conservatively. In particular, the held-out
analysis does not establish predictive discrimination or cell-line specificity,
and the curated cross-organism examples do not establish organism-level
equivalence. Their purpose is to expose where formal model agreement aligns, or
does not align, with distinct structural and empirical evidence layers.

The complete implementation, source models, hash-verified public inputs,
machine-readable outputs, unit tests, executed notebook, and commands for
independent reproduction are publicly available at
<https://github.com/cero1979/BisimulationMol>. The submission source uses the
unmodified World Scientific JBCB class and bibliography style.

I confirm that this manuscript is original, is not under consideration by
another journal, and has been approved by the author. I declare no competing
interests and no specific funding for this work.

Thank you for your consideration.

Sincerely,

Carlos Ramirez Ovalle
Department of Natural Sciences and Mathematics
Pontificia Universidad Javeriana Cali
Cali, Colombia
carlosovalle@javerianacali.edu.co
