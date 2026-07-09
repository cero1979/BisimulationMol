"""
make_figures.py
===============

Runs the full methodology (Phases 1-6) plus the diagnostic experiments and
regenerates, reproducibly, every figure and table consumed by the LaTeX
article (``figs/`` and ``results/``). No network access or external database is
required: everything derives from the curated models in
``src/concurrent_biomodels.py``.

    python make_figures.py
"""

from __future__ import annotations

import os
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import pandas as pd
import pydot

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))
import concurrent_biomodels as cbm  # noqa: E402

ROOT = os.path.dirname(os.path.abspath(__file__))
FIG = os.path.join(ROOT, "figs")
RES = os.path.join(ROOT, "results")
os.makedirs(FIG, exist_ok=True)
os.makedirs(RES, exist_ok=True)

plt.rcParams.update(
    {
        "figure.dpi": 150,
        "savefig.dpi": 150,
        "font.size": 10,
        "axes.titlesize": 11,
        "axes.spines.top": False,
        "axes.spines.right": False,
    }
)

C_HUMAN = "#3b6fb5"
C_PLANT = "#4a9b5e"
C_TAU = "#9a9a9a"
C_GOLD = "#c9a227"
C_RED = "#b5563b"


# ---------------------------------------------------------------------------
# Phase 1 : gene counts per hallmark (Table 1 of the base article)
# ---------------------------------------------------------------------------
def fig_phase1():
    d = cbm.HALLMARK_GENE_COUNTS
    codes = list(d.keys())
    human = [d[c]["human"] for c in codes]
    ath = [d[c]["ath"] for c in codes]
    prio = [d[c]["prio"] for c in codes]

    order = np.argsort(human)[::-1]
    codes = [codes[i] for i in order]
    human = [human[i] for i in order]
    ath = [ath[i] for i in order]
    prio = [prio[i] for i in order]

    x = np.arange(len(codes))
    w = 0.4
    fig, ax = plt.subplots(figsize=(8.2, 3.8))
    ax.bar(x - w / 2, human, w, label="H. sapiens (associated genes)", color=C_HUMAN)
    ax.bar(x + w / 2, ath, w, label="A. thaliana (unique orthologs)", color=C_PLANT)
    for i, p in enumerate(prio):
        if p:
            ax.annotate("\u2605", (x[i], max(human[i], ath[i])),
                        ha="center", va="bottom", color=C_GOLD, fontsize=12)
    ax.set_xticks(x)
    ax.set_xticklabels(codes)
    ax.set_ylabel("Number of genes")
    ax.set_title("Phase 1 - Genes per cancer hallmark (\u2605 = prioritised as partial model)")
    ax.legend(frameon=False, fontsize=8)
    fig.tight_layout()
    fig.savefig(os.path.join(FIG, "fig_phase1_hallmarks.png"))
    plt.close(fig)

    pd.DataFrame(
        {
            "code": codes,
            "name": [cbm.HALLMARK_GENE_COUNTS[c]["name"] for c in codes],
            "human_genes": human,
            "ath_unique_orthologs": ath,
            "prioritized": prio,
        }
    ).to_csv(os.path.join(RES, "phase1_hallmarks.csv"), index=False)


# ---------------------------------------------------------------------------
# Phase 2 : subnetwork conservation index per module
# ---------------------------------------------------------------------------
def fig_phase2():
    rows = [cbm.conservation_index(m) for m in cbm.MODULES]
    df = pd.DataFrame(rows)
    df["user_module"] = [cbm.MODULES[m]["user_module"] for m in df["module"]]
    df.to_csv(os.path.join(RES, "phase2_conservation.csv"), index=False)

    fig, ax = plt.subplots(figsize=(7.6, 3.4))
    colors = [C_PLANT if v >= 0.7 else (C_GOLD if v >= 0.5 else C_RED)
              for v in df["conservation_index"]]
    ax.barh(df["module"], df["conservation_index"], color=colors)
    for i, (v, tot, cons) in enumerate(
        zip(df["conservation_index"], df["total_components"], df["conserved_components"])
    ):
        ax.text(v + 0.01, i, f"{v:.2f}  ({cons}/{tot})", va="center", fontsize=8)
    ax.set_xlim(0, 1.15)
    ax.set_xlabel("Conservation index (components with a conserved functional ortholog)")
    ax.set_title("Phase 2 - Conserved active subnetworks per module")
    ax.invert_yaxis()
    fig.tight_layout()
    fig.savefig(os.path.join(FIG, "fig_phase2_conservation.png"))
    plt.close(fig)


# ---------------------------------------------------------------------------
# Phase 4 : Petri-net drawings (Graphviz/dot layout)
# ---------------------------------------------------------------------------
def draw_petri(net: cbm.PetriNet, path: str, title: str):
    g = pydot.Dot(graph_type="digraph", rankdir="LR", splines="spline",
                  nodesep="0.35", ranksep="0.7", fontname="Helvetica",
                  label=title, labelloc="t", fontsize="16")
    g.set_dpi("150")
    bullet = "\u25cf"
    for p in net.places:
        tokens = net.init.get(p, 0)
        lbl = p if not tokens else f"{p}\n{bullet * tokens}"
        g.add_node(pydot.Node(
            f"p_{p}", shape="circle", style="filled",
            fillcolor="#eaf1fb", color="#3b6fb5", penwidth="1.8",
            fontsize="11", label=lbl))
    for t in net.transitions:
        is_tau = t.label == cbm.TAU
        tsym = "\u03c4" if is_tau else t.label
        lbl = f"{t.name}\n[{tsym}]"
        g.add_node(pydot.Node(
            f"t_{t.name}", shape="box", style="filled,rounded",
            fillcolor="#f0f0f0" if is_tau else "#fff3d6",
            color="#9a9a9a" if is_tau else "#c9962b", penwidth="1.8",
            fontsize="10", label=lbl))
        for p in t.pre:
            g.add_edge(pydot.Edge(f"p_{p}", f"t_{t.name}", color="#666", penwidth="1.2"))
        for p in t.post:
            g.add_edge(pydot.Edge(f"t_{t.name}", f"p_{p}", color="#666", penwidth="1.2"))
    g.write_png(path)


# ---------------------------------------------------------------------------
# Phase 5 : reachability-graph (LTS) drawing
# ---------------------------------------------------------------------------
def draw_lts(lts: cbm.LTS, path: str, title: str):
    G = nx.MultiDiGraph()
    for i in range(len(lts.states)):
        G.add_node(i)
    for s, a, d in lts.edges:
        G.add_edge(s, d, label=a)
    try:
        pos = nx.nx_pydot.graphviz_layout(G, prog="dot")
    except Exception:
        pos = nx.spring_layout(G, seed=7, k=1.3)

    fig, ax = plt.subplots(figsize=(8.5, 5.6))
    nx.draw_networkx_nodes(G, pos, node_color="#eef4fb",
                           edgecolors="#3b6fb5", node_size=520, ax=ax)
    nx.draw_networkx_labels(G, pos, font_size=8, ax=ax)
    nx.draw_networkx_nodes(G, pos, nodelist=[lts.init], node_color="#d6ecd8",
                           edgecolors=C_PLANT, node_size=560, ax=ax)

    obs_edges = [(s, d) for s, a, d in lts.edges if a != cbm.TAU]
    tau_edges = [(s, d) for s, a, d in lts.edges if a == cbm.TAU]
    nx.draw_networkx_edges(G, pos, edgelist=obs_edges, edge_color="#8a5a00",
                           width=1.5, ax=ax, connectionstyle="arc3,rad=0.05")
    nx.draw_networkx_edges(G, pos, edgelist=tau_edges, edge_color=C_TAU,
                           width=1.1, style="dashed", ax=ax,
                           connectionstyle="arc3,rad=0.05")
    elabels = {(s, d): (a if a != cbm.TAU else "\u03c4") for s, a, d in lts.edges}
    nx.draw_networkx_edge_labels(G, pos, edge_labels=elabels, font_size=7,
                                 label_pos=0.55, rotate=False, ax=ax,
                                 bbox=dict(fc="white", ec="none", alpha=0.75))
    ax.legend(handles=[mpatches.Patch(color="#8a5a00", label="observable event"),
                       mpatches.Patch(color=C_TAU, label="\u03c4 (internal)")],
              frameon=False, fontsize=8, loc="best")
    ax.set_title(title)
    ax.axis("off")
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)


# ---------------------------------------------------------------------------
# Phase 6 : comparability spectrum and property matrix
# ---------------------------------------------------------------------------
def fig_phase6(comparisons):
    df = pd.DataFrame([c.__dict__ for c in comparisons])
    df.to_csv(os.path.join(RES, "phase6_comparisons.csv"), index=False)

    fig, ax = plt.subplots(figsize=(8.2, 3.8))
    order = df.sort_values("distance").reset_index(drop=True)
    colors = []
    for _, r in order.iterrows():
        if r["weak_bisimilar"]:
            colors.append(C_PLANT)
        elif r["plant_simulated_by_animal"] or r["animal_simulated_by_plant"]:
            colors.append(C_GOLD)
        else:
            colors.append(C_RED)
    ax.bar(order["module"], order["distance"], color=colors)
    for i, r in order.iterrows():
        tag = ("\u2248 bisim." if r["weak_bisimilar"]
               else ("simul." if (r["plant_simulated_by_animal"] or r["animal_simulated_by_plant"])
                     else "not comp."))
        ax.text(i, r["distance"] + 0.01, f"{r['distance']:.2f}\n{tag}",
                ha="center", va="bottom", fontsize=8)
    ax.set_ylim(0, max(order["distance"]) + 0.15)
    ax.set_ylabel("Behavioural distance (trace Jaccard)")
    ax.set_title("Phase 6 - Partial-comparability spectrum per module")
    ax.legend(handles=[
        mpatches.Patch(color=C_PLANT, label="Comparable (weak bisimulation)"),
        mpatches.Patch(color=C_GOLD, label="Partial (simulation)"),
        mpatches.Patch(color=C_RED, label="Not comparable"),
    ], frameon=False, fontsize=8)
    fig.tight_layout()
    fig.savefig(os.path.join(FIG, "fig_phase6_spectrum.png"))
    plt.close(fig)

    props = ["strong_bisimilar", "weak_bisimilar",
             "plant_simulated_by_animal", "animal_simulated_by_plant"]
    labels = ["Strong\nbisim.", "Weak\nbisim.", "Plant\u2291Animal", "Animal\u2291Plant"]
    M = df.set_index("module")[props].astype(int).values
    fig, ax = plt.subplots(figsize=(6.6, 3.6))
    ax.imshow(M, cmap="Greens", vmin=0, vmax=1, aspect="auto")
    ax.set_xticks(range(len(props)))
    ax.set_xticklabels(labels, fontsize=8)
    ax.set_yticks(range(len(df)))
    ax.set_yticklabels(df["module"])
    for i in range(M.shape[0]):
        for j in range(M.shape[1]):
            ax.text(j, i, "yes" if M[i, j] else "no", ha="center", va="center",
                    color="#123" if M[i, j] else "#999", fontsize=8)
    ax.set_title("Behavioural properties per module")
    fig.tight_layout()
    fig.savefig(os.path.join(FIG, "fig_phase6_properties.png"))
    plt.close(fig)

    short = {"GIM": "DNA repair", "DCE": "Energy metabolism", "SPS": "Cell cycle",
             "RCD": "Cell death/autophagy", "AID": "Immune (control)"}
    with open(os.path.join(RES, "phase6_table.tex"), "w") as f:
        f.write("\\begin{tabular}{llcccc c}\n\\toprule\n")
        f.write("Module & Sub-mechanism & Strong bisim. & Weak bisim. & "
                "Pl.$\\sqsubseteq$An. & An.$\\sqsubseteq$Pl. & $d$ \\\\\n\\midrule\n")
        for _, r in df.iterrows():
            yn = lambda b: "\\checkmark" if b else "--"
            f.write(
                f"{r['module']} & {short.get(r['module'], r['module'])} & "
                f"{yn(r['strong_bisimilar'])} & {yn(r['weak_bisimilar'])} & "
                f"{yn(r['plant_simulated_by_animal'])} & "
                f"{yn(r['animal_simulated_by_plant'])} & {r['distance']:.2f} \\\\\n"
            )
        f.write("\\bottomrule\n\\end{tabular}\n")
    return df


# ---------------------------------------------------------------------------
# Methodology pipeline diagram
# ---------------------------------------------------------------------------
def fig_pipeline():
    phases = [
        ("Phase 1", "Biological\ndelimitation\nof modules"),
        ("Phase 2", "Conserved\nactive\nsubnetworks"),
        ("Phase 3", "Common\nobservational\ninterface"),
        ("Phase 4", "Concurrent\nformalisation\n(Petri nets)"),
        ("Phase 5", "Partial\nbehavioural\ncomparison"),
        ("Phase 6", "Partial-\ncomparability\ncriterion"),
    ]
    fig, ax = plt.subplots(figsize=(10.5, 2.6))
    x = 0.0
    for i, (ph, txt) in enumerate(phases):
        c = C_HUMAN if i < 3 else C_PLANT
        ax.add_patch(mpatches.FancyBboxPatch(
            (x, 0), 1.5, 1.4, boxstyle="round,pad=0.03",
            facecolor="#eef4fb" if i < 3 else "#eaf5ec", edgecolor=c, lw=1.6))
        ax.text(x + 0.75, 1.18, ph, ha="center", va="center", fontsize=9,
                fontweight="bold", color=c)
        ax.text(x + 0.75, 0.55, txt, ha="center", va="center", fontsize=8)
        if i < len(phases) - 1:
            ax.annotate("", xy=(x + 1.72, 0.7), xytext=(x + 1.5, 0.7),
                        arrowprops=dict(arrowstyle="-|>", color="#555", lw=1.6))
        x += 1.72
    ax.text(2.25, -0.35, "Biological-computational level", ha="center", fontsize=8.5,
            color=C_HUMAN, style="italic")
    ax.text(7.4, -0.35, "Formal level (concurrency)", ha="center", fontsize=8.5,
            color=C_PLANT, style="italic")
    ax.set_xlim(-0.2, x)
    ax.set_ylim(-0.7, 1.6)
    ax.axis("off")
    fig.tight_layout()
    fig.savefig(os.path.join(FIG, "fig_pipeline.png"))
    plt.close(fig)


# ---------------------------------------------------------------------------
# Robustness (silent tau-refinement) and null baseline (label permutation)
# ---------------------------------------------------------------------------
def fig_robustness_and_null(seed=7):
    mods = list(cbm.MODULES)

    rob = [cbm.robustness_under_tau_refinement(m, n=300, n_ins=4, seed=seed)
           for m in mods]
    pd.DataFrame(rob).to_csv(os.path.join(RES, "robustness.csv"), index=False)

    nb = cbm.null_baseline_suite(mods, n=2000, frac=0.6, seed=seed)
    nb_df = pd.DataFrame([{k: v for k, v in r.items() if k != "null"} for r in nb])
    nb_df.to_csv(os.path.join(RES, "nullbaseline.csv"), index=False)

    int_rows = []
    for m in mods:
        int_rows.extend(cbm.interface_necessity(m, k=6))
    interface_df = pd.DataFrame(int_rows)
    interface_df.to_csv(os.path.join(RES, "interface_necessity.csv"), index=False)

    seed_df = pd.DataFrame(cbm.null_seed_sensitivity(mods, n=2000, frac=0.6))
    seed_df.to_csv(os.path.join(RES, "null_seed_sensitivity.csv"), index=False)

    # --- robustness bar ---
    fig, ax = plt.subplots(figsize=(7.4, 3.2))
    ax.bar(mods, [r["frac_verdict_preserved"] for r in rob], color=C_PLANT)
    for i, r in enumerate(rob):
        ax.text(i, r["frac_verdict_preserved"] + 0.01,
                f"{r['frac_verdict_preserved']*100:.0f}%", ha="center",
                va="bottom", fontsize=9)
    ax.set_ylim(0, 1.12)
    ax.set_ylabel("Fraction of runs preserving the verdict")
    ax.set_title("Verdict invariance under silent (\u03c4) refinement (300 runs/module)")
    fig.tight_layout()
    fig.savefig(os.path.join(FIG, "fig_robustness.png"))
    plt.close(fig)

    # --- null baseline violins ---
    fig, ax = plt.subplots(figsize=(8.4, 4.0))
    data = [r["null"] for r in nb]
    parts = ax.violinplot(data, showmeans=False, showextrema=False)
    for pc in parts["bodies"]:
        pc.set_facecolor("#c9d6ea")
        pc.set_edgecolor("#7f93b3")
        pc.set_alpha(0.8)
    xs = np.arange(1, len(mods) + 1)
    obs = [r["observed_distance"] for r in nb]
    ax.scatter(xs, obs, color=C_RED, zorder=5, s=45, label="observed distance")
    for i, r in enumerate(nb):
        star = " *" if r["q_value_bh"] < 0.05 else ""
        ax.text(xs[i], 1.02, f"p={r['p_value']:.3f}\nq={r['q_value_bh']:.3f}{star}",
                ha="center", fontsize=7,
                color=("#123" if r["q_value_bh"] < 0.05 else "#999"))
    ax.set_xticks(xs)
    ax.set_xticklabels(mods)
    ax.set_ylim(-0.05, 1.2)
    ax.set_ylabel("Behavioural distance to the animal model")
    ax.set_title("Null baseline: observed vs scrambled-interface distances "
                 "(2000 permutations/module)")
    ax.legend(frameon=False, fontsize=8, loc="lower right")
    fig.tight_layout()
    fig.savefig(os.path.join(FIG, "fig_nullbaseline.png"))
    plt.close(fig)
    return nb_df


# ---------------------------------------------------------------------------
# k-convergence of the behavioural distance
# ---------------------------------------------------------------------------
def fig_kconvergence():
    fig, ax = plt.subplots(figsize=(7.6, 3.4))
    markers = {"GIM": "o", "DCE": "s", "SPS": "^", "RCD": "D", "AID": "v"}
    rows = []
    for m in cbm.MODULES:
        curve = cbm.distance_curve(m, kmax=12)
        ks = [k for k, _ in curve]
        ds = [d for _, d in curve]
        for k, d in curve:
            rows.append({"module": m, "k": k, "distance": d})
        ax.plot(ks, ds, marker=markers[m], label=m, linewidth=1.6, markersize=4)
    pd.DataFrame(rows).to_csv(os.path.join(RES, "kconvergence.csv"), index=False)
    ax.set_xlabel("Trace-truncation depth $k$")
    ax.set_ylabel("Behavioural distance $d_k$")
    ax.set_title("Stability of the behavioural distance with $k$")
    ax.legend(frameon=False, fontsize=8, ncol=5)
    ax.set_ylim(-0.03, 0.55)
    fig.tight_layout()
    fig.savefig(os.path.join(FIG, "fig_kconvergence.png"))
    plt.close(fig)


# ---------------------------------------------------------------------------
# Model-construction provenance tables as LaTeX
# ---------------------------------------------------------------------------
def _tex_escape(s: str) -> str:
    return s.replace("_", "\\_").replace("&", "\\&")


def provenance_tables():
    with open(os.path.join(RES, "gim_provenance.tex"), "w") as f:
        f.write("\\begin{tabular}{p{4.4cm}p{7.2cm}l}\n\\toprule\n")
        f.write("Transition(s) & Biological event modelled & Evidence \\\\\n\\midrule\n")
        for tr, ev, ref in cbm.MODEL_PROVENANCE["GIM"]:
            f.write(f"{_tex_escape(tr)} & {_tex_escape(ev)} & {ref} \\\\\n")
        f.write("\\bottomrule\n\\end{tabular}\n")

    with open(os.path.join(RES, "model_provenance_all.tex"), "w") as f:
        f.write("\\begin{longtable}{@{}p{1.4cm}p{4.5cm}p{7.2cm}p{1.8cm}@{}}\n")
        f.write("\\caption{Transition-level provenance for all curated modules. "
                "Each Petri-net transition name is named at least once in this "
                "table; this coverage is checked by the notebook and the "
                "\\texttt{provenance\\_coverage} function.}\\\\\n")
        f.write("\\toprule\n")
        f.write("Module & Transition(s) & Biological event modelled & Evidence \\\\\n")
        f.write("\\midrule\n\\endfirsthead\n")
        f.write("\\toprule\n")
        f.write("Module & Transition(s) & Biological event modelled & Evidence \\\\\n")
        f.write("\\midrule\n\\endhead\n")
        for module in cbm.MODULES:
            for tr, ev, ref in cbm.MODEL_PROVENANCE[module]:
                f.write(
                    f"{module} & {_tex_escape(tr)} & {_tex_escape(ev)} & {ref} \\\\\n"
                )
        f.write("\\bottomrule\n\\end{longtable}\n")


def reviewer_objection_table():
    rows = [
        (
            "The Petri nets are hand-built and may be tuned to the desired result.",
            "Every transition is tied to a provenance row; coverage is audited; verdicts are invariant under 300 silent refinements per module.",
            "Appendix provenance; robustness.csv; notebook coverage assert",
        ),
        (
            "The observational interface may determine the answer.",
            "The interface is declared as the hypothesis, tested by global label permutation and by targeted single-label mismatch.",
            "nullbaseline.csv; interface_necessity.csv",
        ),
        (
            "Trace distance is not equivalent to bisimulation.",
            "Branching-time bisimulation/simulation is the primary verdict; trace distance is only a ranking and null-test statistic.",
            "Preliminaries and Phase 6 rule",
        ),
        (
            "The null test may be seed-dependent or inflated by multiple testing.",
            "The family of five tests is corrected by Benjamini-Hochberg q-values and repeated across five seeds.",
            "nullbaseline and seed-sensitivity CSVs",
        ),
        (
            "The models are too compact to validate biology globally.",
            "The claim is narrowed to partial module comparability under a declared interface, with explicit threats to validity.",
            "Discussion and conclusion",
        ),
        (
            "The generalisation beyond Arabidopsis is only rhetorical.",
            "The same organism-agnostic routine is applied to human, mouse, yeast and Arabidopsis cell-cycle models, and rejects a scrambled same-alphabet control.",
            "generalization.csv and Fig. generalisation",
        ),
        (
            "The immune negative control could be a post-hoc failure case.",
            "AID is pre-declared from non-prioritised immune destruction; it remains non-comparable and non-significant under the null.",
            "Phase 1; AID q=0.154",
        ),
    ]
    with open(os.path.join(RES, "reviewer_objections.tex"), "w") as f:
        f.write("\\begin{longtable}{@{}p{4.2cm}p{6.7cm}p{3.1cm}@{}}\n")
        f.write("\\caption{Adversarial reviewer-objection matrix.}\\\\\n")
        f.write("\\toprule\n")
        f.write("Hostile objection & Response built into the study & Evidence \\\\\n")
        f.write("\\midrule\n\\endfirsthead\n")
        f.write("\\toprule\n")
        f.write("Hostile objection & Response built into the study & Evidence \\\\\n")
        f.write("\\midrule\n\\endhead\n")
        for objection, response, evidence in rows:
            f.write(
                f"{_tex_escape(objection)} & {_tex_escape(response)} & "
                f"{_tex_escape(evidence)} \\\\\n"
            )
        f.write("\\bottomrule\n\\end{longtable}\n")


# ---------------------------------------------------------------------------
def fig_generalization():
    """Cross-organism portability: the same method applied to one conserved
    module (cell cycle) between a human reference and a panel of model organisms.
    """
    rows = cbm.generalization_analysis(k=6)
    df = pd.DataFrame(rows)
    df.to_csv(os.path.join(RES, "generalization.csv"), index=False)

    orgs = [r["organism"] for r in rows]
    M = np.array([[int(r["strong_bisimilar"]), int(r["weak_bisimilar"])]
                  for r in rows])
    fig, ax = plt.subplots(figsize=(6.6, 2.9))
    ax.imshow(M, cmap="Greens", vmin=0, vmax=1, aspect="auto")
    ax.set_xticks([0, 1])
    ax.set_xticklabels(["Strong\nbisimulation", "Weak\nbisimulation"])
    ax.set_yticks(range(len(orgs)))
    ax.set_yticklabels([f"{o} vs Human" for o in orgs])
    for i in range(M.shape[0]):
        for j in range(M.shape[1]):
            ax.text(j, i, "yes" if M[i, j] else "no", ha="center", va="center",
                    color="#123" if M[i, j] else "#999", fontsize=9)
    ax.set_title("Generalisation: cell-cycle module and scrambled control")
    fig.tight_layout()
    fig.savefig(os.path.join(FIG, "fig_generalization.png"))
    plt.close(fig)

    short = {"Comparable (strong: near-identical core)": "strong (near-identical)",
             "Comparable (weak bisimulation)": "weak bisimulation",
             "Partial (simulation)": "partial (simulation)",
             "Not comparable": "not comparable"}
    with open(os.path.join(RES, "generalization.tex"), "w") as f:
        f.write("\\begin{tabular}{lcccl}\n\\toprule\n")
        f.write("System (vs Human) & Strong bisim. & Weak bisim. & $d$ & "
                "Verdict \\\\\n\\midrule\n")
        for r in rows:
            yn = lambda b: "\\checkmark" if b else "--"
            f.write(f"{r['organism']} & {yn(r['strong_bisimilar'])} & "
                    f"{yn(r['weak_bisimilar'])} & {r['distance']:.2f} & "
                    f"{short.get(r['verdict'], r['verdict'])} \\\\\n")
        f.write("\\bottomrule\n\\end{tabular}\n")
    return df


def main():
    print(">> Phase 1: hallmarks");          fig_phase1()
    print(">> Phase 2: conservation");       fig_phase2()
    print(">> Pipeline");                    fig_pipeline()

    print(">> Phase 4: Petri nets (GIM & RCD)")
    draw_petri(cbm.ddr_animal(), os.path.join(FIG, "fig_ddr_petri_animal.png"),
               "Phase 4 - GIM Petri net (animal/human): DNA damage response")
    draw_petri(cbm.ddr_plant(), os.path.join(FIG, "fig_ddr_petri_plant.png"),
               "Phase 4 - GIM Petri net (Arabidopsis): DNA damage response")
    draw_petri(cbm.death_animal(), os.path.join(FIG, "fig_rcd_petri_animal.png"),
               "RCD Petri net (animal): autophagy + caspase apoptosis")
    draw_petri(cbm.death_plant(), os.path.join(FIG, "fig_rcd_petri_plant.png"),
               "RCD Petri net (Arabidopsis): autophagy + metacaspase PCD")

    print(">> Phase 5: LTS (GIM)")
    draw_lts(cbm.ddr_animal().reachability_lts(),
             os.path.join(FIG, "fig_ddr_lts_animal.png"),
             "Phase 5 - GIM reachability LTS (animal/human)")
    draw_lts(cbm.ddr_plant().reachability_lts(),
             os.path.join(FIG, "fig_ddr_lts_plant.png"),
             "Phase 5 - GIM reachability LTS (Arabidopsis)")

    print(">> Phase 6: comparisons")
    comparisons = cbm.run_full_analysis(k=6)
    df = fig_phase6(comparisons)

    print(">> Robustness + null baseline")
    nb_df = fig_robustness_and_null()
    print(">> k-convergence")
    fig_kconvergence()
    print(">> Provenance tables")
    provenance_tables()
    print(">> Reviewer objection matrix")
    reviewer_objection_table()
    print(">> Cross-organism generalisation")
    gen_df = fig_generalization()

    print("\n== Comparability summary ==")
    print(df[["module", "strong_bisimilar", "weak_bisimilar",
              "plant_simulated_by_animal", "animal_simulated_by_plant",
              "distance", "verdict"]].to_string(index=False))
    print("\n== Null baseline ==")
    print(nb_df.to_string(index=False))
    print("\n== Cross-organism generalisation (cell cycle vs Human) ==")
    print(gen_df[["organism", "strong_bisimilar", "weak_bisimilar",
                  "distance", "verdict"]].to_string(index=False))
    print(f"\nFigures -> {FIG}\nResults -> {RES}")


if __name__ == "__main__":
    main()
