"""Assemble R2 from the preserved supplied R1 and reviewed replacement sections.

The generated main TeX is self-contained, including the inline bibliography.
Historical R1 sources, artwork and response are never changed.
"""
from pathlib import Path
import difflib
import hashlib
import json
import re
import shutil

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "revision_R2"
BASE = OUT / "original_R1"
TITLE = "Locating resolution-dependent behavioral correspondence in qualitative DNA-damage response models"


def section(name):
    return (OUT / "sections" / (name + ".tex")).read_text().strip() + "\n\n"


def bibliography_for(body, bibliography):
    """Keep inline entries in first-citation order after narrative relocation."""
    pre, rest = bibliography.split("\\bibitem", 1)
    entries = {}
    for entry in re.split(r"(?=\\bibitem\{)", "\\bibitem" + rest):
        match = re.match(r"\\bibitem\{([^}]+)\}", entry)
        if match:
            entries[match[1]] = entry.split("\\end{thebibliography}")[0].strip() + "\n\n"
    keys = []
    for cite in re.findall(r"\\cite\{([^}]+)\}", body):
        for key in cite.split(","):
            key = key.strip()
            if key not in keys:
                keys.append(key)
    missing = set(keys) - set(entries)
    if missing:
        raise ValueError(f"Missing bibliography: {missing}")
    return pre + "".join(entries[k] for k in keys) + "\\end{thebibliography}\n"


def assemble():
    original = (BASE / "main_jbcb_R1.tex").read_text()
    def between(start, end):
        return original[original.index(start):original.index(end)]
    prefix = original[:original.index("\\begin{abstract}")]
    prefix = prefix.replace("\\documentclass{ws-jbcb}",
                            "\\documentclass{ws-jbcb}\n\\setlength{\\paperheight}{11in}")
    oldtitle = "A formal and reproducible framework for auditing observable behavior in qualitative biological network models"
    prefix = prefix.replace(oldtitle, TITLE).replace(
        "A formal and reproducible framework for auditing observable behavior in\nqualitative biological network models", TITLE)
    prefix = prefix.replace("Formal and reproducible audit of biological network models",
                            "Resolution-dependent correspondence in DNA-damage models")
    prefix = prefix.replace(
        "pdfkeywords={qualitative biological networks, Petri nets, labeled transition systems, weak bisimulation, model checking, Boolean networks}",
        "pdfkeywords={DNA-damage response, observational resolution, qualitative biological networks, model comparison, Petri nets, weak bisimulation}")
    biology = between("\\section{Biological network applications}", "\\subsection{GIM:")
    biology = biology.replace("Biological network applications", "Biological comparison problem and models")
    biology += (
        "The interfaces are curated functional abstractions, not experimentally calibrated\n"
        "observation operators. Their order was fixed for this comparison from known\n"
        "mechanisms; it does not constitute a blinded prediction. The plant and animal\n"
        "nets are small safe interleaving encodings, not complete DDR pathways.\n\n")
    method = between("\\section{Formal framework", "\\subsection{Fixed-point computation")
    method = method.replace("Formal framework for observable biological-model comparison", "Computational comparison method")
    method = method.replace("Under standard interleaving semantics,", "Under standard interleaving semantics,\\cite{Murata1989}")
    method = method.replace("Exact weak-trace results in this study come only\nfrom mCRL2 or from a finite construction for which the complete language is\nenumerated analytically.",
                            "Exact weak-trace results come from mCRL2, acyclic path enumeration,\nor finite subset-product exploration without a depth cutoff; none is inferred\nfrom a truncated distance.")
    method += between("\\subsection{Computational implementation}", "\\section{Computational implementation")
    method += (
        "The finite relation-deletion theorem and the strict hierarchy underlying\n"
        "this reporting priority are proved in \\ref{app:formal}.\n"
        "Example~\\ref{ex:branching} provides an explicit simulation witness and\n"
        "a failed-successor proof for equal traces with one-way simulation.\n"
        "PN-GDDA, LTS-GDA and trace distances answer complementary diagnostic\n"
        "questions; their definitions and implementation checks are retained in\n"
        "Supplementary Validation, Section~S1.\n\n")
    supporting = between("\\subsection{Secondary curated comparisons}", "\\section{Discussion}")
    supporting = supporting.replace("\\subsection{Secondary curated comparisons}", "\\section{Supporting curated comparisons}")
    formal = between("\\subsection{Fixed-point computation", "\\subsection{Computational implementation}")
    formal = formal.replace("\\subsection{Fixed-point computation and formal properties}\n\\label{sec:fixed-point}",
                            "\\section{Mathematical properties and quantifier audit}\\label{app:formal}\n\\label{sec:fixed-point}")
    formal = formal[:formal.index("\\begin{example}[Equal traces")] + section("example1")
    hierarchy_table = r"""
\begin{table}[t]
\tbl{Distinct witnesses for the three failed converses. All pairs have equal
exact weak-trace languages; $X\preceq Y$ means $Y$ simulates $X$.
\label{tab:hierarchy-witnesses}}{
\begin{tabular}{@{}p{1.75in}p{1.6in}p{1.3in}@{}}
\toprule
Converse refuted & Witness pair $(X,Y)$ & Decisive properties\\
\colrule
Weak implies strong bisimilarity & $a.0$, $a.\tau.0$ & weak, not strong\\
Mutual simulation implies weak bisimilarity & $a.(b+c)+a.b$, $a.(b+c)$ & both directions, not weak\\
Exact trace equality implies mutual simulation & late choice, early choice & early$\preceq$late only\\
\botrule
\end{tabular}}
\end{table}

For the middle row, write $x_{bc},x_b$ for the two $a$-successors of $X$ and
$y_{bc}$ for the sole $a$-successor of $Y$. A simulation from $X$ to $Y$
relates both $x_{bc}$ and $x_b$ to $y_{bc}$, with corresponding terminal
pairs. A simulation from $Y$ to $X$ relates $y_{bc}$ only to $x_{bc}$.
Both initial pairs therefore survive. A bisimulation would additionally need
to match $X$'s transition to $x_b$ with $y_{bc}$; the latter's $c$-move has
no counterpart at $x_b$. This witness concerns only the middle converse,
not the trace-equality converse refuted by Example~\ref{ex:branching}.

"""
    formal = formal.replace("\\begin{proposition}[Controlled silent edge refinement]", hierarchy_table + "\\begin{proposition}[Controlled silent edge refinement]")
    nets = between("\\section{Detailed GIM Petri-net encodings}", "\\section*{Data and code availability}")
    net_heading = nets[:nets.index("\n\n")]
    nets = net_heading + (
        "\n\nFigures~\\ref{fig:gim-animal-net} and \\ref{fig:gim-plant-net} show the\n"
        "fixed executable nets; the three interfaces change only transition labels.\n\n") + nets[nets.index("\\clearpage"):]
    nets = nets.replace("R1_Fig5.pdf", "R2_Fig3.pdf").replace("R1_Fig6.pdf", "R2_Fig4.pdf")
    declarations = between("\\section*{Data and code availability}", "\\begin{thebibliography}")
    declarations = declarations.replace("The repository documents", "The second-revision source and audits are in \\texttt{revision\\_R2/}.\nThe repository documents")
    bib = original[original.index("\\begin{thebibliography}"):original.index("\\end{thebibliography}") + len("\\end{thebibliography}")]
    body = (prefix + "\\begin{abstract}\n" + section("abstract") + "\\end{abstract}\n\n"
            + "\\keywords{DNA-damage response; observational resolution; qualitative biological networks; model comparison; Petri nets; weak bisimulation.}\n\n"
            + section("introduction") + biology + method + section("gim_results") + supporting
            + section("supporting_validation") + section("discussion_conclusion")
            + "\\appendix\n" + formal + nets + declarations)
    main = body + bibliography_for(body, bib) + "\n\\end{document}\n"
    (OUT / "main_jbcb_R2.tex").write_text(main)
    (OUT / "main_jbcb_R1_to_R2.diff").write_text("".join(difflib.unified_diff(
        original.splitlines(True), main.splitlines(True), fromfile="main_jbcb_R1.tex", tofile="main_jbcb_R2.tex")))
    shutil.copy2(BASE / "ws-jbcb.cls", OUT / "ws-jbcb.cls")
    for old, new in [("R1_Fig5.pdf", "R2_Fig3.pdf"), ("R1_Fig6.pdf", "R2_Fig4.pdf"),
                     ("R1_Fig2.pdf", "R2_SFig1.pdf"), ("R1_Fig4.pdf", "R2_SFig2.pdf")]:
        shutil.copy2(BASE / old, OUT / new)
    supplement = between("\\section{Computational implementation", "\\section{Biological network applications}")
    supplement = supplement.replace("Computational implementation and formal/software verification", "Formal and software verification")
    supplement += between("\\subsection{Cross-format ingestion", "\\subsection{Secondary curated comparisons}")
    supplement = supplement.replace("\\subsection{Cross-format ingestion and execution controls}", "\\section{Cross-format ingestion and execution controls}")
    supplement = supplement.replace("\\subsection{Exploratory HPN-DREAM/CASPOTS held-out analysis}", "\\section{Exploratory HPN-DREAM/CASPOTS held-out analysis}")
    supplement = supplement.replace("Example~\\ref{ex:branching}", "Example~1 of the main article")
    supplement = supplement.replace("Theorem~\\ref{thm:fixed-point}", "Theorem~1 of the main article")
    supplement = supplement.replace("R1_Fig2.pdf", "R2_SFig1.pdf").replace("R1_Fig4.pdf", "R2_SFig2.pdf")
    supplement = supplement.replace("every Holmes 1.1.1 topology/root assignment", "every inspected Holmes 1.1.1 topology/root assignment")
    supplement = supplement.replace(
        "Its used interface does not expose the weak\nsimulation preorder, so no one-way simulation is attributed to mCRL2.",
        "Its interface does not expose a general weak-simulation preorder. For\nthe tau-free Example~1 and middle strictness witness only, R2 additionally\nuses its strong-simulation preorder, which coincides with weak simulation\nwhen neither input has silent transitions; both directions agree. No such\nweak-preorder claim is made for systems containing silent transitions.")
    exhaustive = json.loads((ROOT / "results/exhaustive_formal_audit_R2.json").read_text())
    supplement += r"""
\section{Second-round quantifier and direction audit}
The production implementation was not changed to conform to a proposed
reinterpretation of simulation. Instead, the R2 audit independently constructs
silent closures and weak targets from raw edges, and grows a least losing set
in simultaneous attacker--defender rounds. It does not call the production
adjacency, closure, weak-step, or relation routines. Exact weak-trace inclusion
is checked by a finite epsilon-NFA subset-product traversal, treating all
original states as accepting, without a depth cutoff.

For Example~1 in the main article, complete acyclic path enumeration also
gives $\{\epsilon,a,ab,ac\}$ on both sides. The supplied five-pair early-to-late
relation satisfies every transfer clause. The reverse calculation first
removes $(\ell_1,e_b)$ because $c$ cannot be matched and $(\ell_1,e_c)$ because
$b$ cannot be matched; the initial pair subsequently has no surviving reply.
The machine-readable deletion certificate records these dependencies.

All three strictness witnesses and 32 ordered model pairs (six synthetic,
three GIM interfaces, five curated modules, and 18 asynchronous/synchronous
HPN comparisons) agree on strong/weak bisimilarity and both weak-simulation
directions between the production code and independent audit. Every synthetic
class still agrees with its construction-level expectation. Direction fields
explicitly state \texttt{left\_simulated\_by\_right} and
\texttt{right\_simulated\_by\_left}.

The complete one-/two-state universe contains 260 named LTSs over
$\{a,\tau\}$ with initial state zero, hence 67,600 ordered pairs. The expanded
audit found no simulation or weak-bisimulation disagreement and no failure of
the hierarchy or trace-inclusion implications. Simulation is reflexive and
transitive on this universe. There are 41,080 weakly bisimilar ordered pairs
and 4,848 mutually simulated but non-bisimilar ordered pairs. No one-way
simulation with exact trace equality occurs in this small universe; the
larger acyclic Example~1 supplies that witness. The finite enumeration
supports software correctness only; it does not replace the general proofs.

Reproduce the new audit using
\texttt{python -m src.formal\_revision\_audit} and
\texttt{python -m unittest tests.test\_formal\_revision\_R2 -v}.
The four JSON/CSV reports in \texttt{results/} include the Example~1
certificate, hierarchy witnesses, all model-pair directions, and exhaustive
counts. The main article's appendix retains all definitions needed for its
claims, the relation-deletion proof, and explicit proofs of the three failed
converses. Detailed Petri nets remain in the main article rather than being
removed during compression of validation material.
"""
    if exhaustive["ordered_lts_pairs"] != 67600 or not exhaustive["all_checks_pass"]:
        raise ValueError("Re-audit supplementary counts after changed results")
    supprefix = prefix[:prefix.index("\\begin{document}")]
    supprefix = supprefix.replace(TITLE, "Supplementary Validation: " + TITLE)
    supprefix += r"""
\renewcommand{\thesection}{S\arabic{section}}
\renewcommand{\thefigure}{S\arabic{figure}}
\renewcommand{\thetable}{S\arabic{table}}
\begin{document}
\markboth{C. Ramirez Ovalle}{Supplementary validation for JBCB-1505 R2}
\catchline{}{}{}{}{}
\title{Supplementary Validation: Resolution-dependent correspondence in DNA-damage models}
\author{Carlos Ramirez Ovalle}
\address{Pontificia Universidad Javeriana Cali, Colombia}
\maketitle
This supplement retains implementation-verification and exploratory-data
details supporting the main biological comparison. It is not independent
biological validation of the curated GIM models.

"""
    suppbody = supprefix + supplement
    (OUT / "Supplementary_Validation_R2.tex").write_text(suppbody + bibliography_for(suppbody, bib) + "\n\\end{document}\n")
    manifest = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(BASE.iterdir()) if p.is_file()}
    (OUT / "baseline_sha256.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print("Assembled R2 manuscript and supplement from preserved R1; inline bibliographies ordered by first citation.")


if __name__ == "__main__":
    assemble()
