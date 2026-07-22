"""
make_figures.py
===============

Runs the full methodology (Phases 1-6) plus the diagnostic experiments and
regenerates, reproducibly, every figure and table consumed by the LaTeX
article (``figs/`` and ``results/``). No network access is required after the
two hash-pinned public GINsim models have been fetched. The independent formal
cross-check requires the ``ltscompare`` executable from mCRL2.

    python make_figures.py
"""

from __future__ import annotations

import json
import os
import shutil
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
import hpn_dream_validation as hpn  # noqa: E402
import method_benchmark as mb  # noqa: E402
import pn_gdda  # noqa: E402
import public_validation as pv  # noqa: E402
import simulation_oracle as simulation_oracle  # noqa: E402

ROOT = os.path.dirname(os.path.abspath(__file__))
FIG = os.path.join(ROOT, "figs")
RES = os.path.join(ROOT, "results")
os.makedirs(FIG, exist_ok=True)
os.makedirs(RES, exist_ok=True)

plt.rcParams.update(
    {
        "figure.dpi": 150,
        "savefig.dpi": 300,
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
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


def save_artwork(fig, png_path: str) -> None:
    """Write a high-resolution preview and an editable vector counterpart."""
    fig.savefig(png_path, dpi=300)
    fig.savefig(os.path.splitext(png_path)[0] + ".pdf")


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
def draw_petri(net: cbm.PetriNet, path: str, _title: str):
    g = pydot.Dot(graph_type="digraph", rankdir="LR", splines="spline",
                  nodesep="0.25", ranksep="0.45", fontname="Helvetica")
    bullet = "\u25cf"
    for p in net.places:
        tokens = net.init.get(p, 0)
        display_place = p.replace("_", "\n")
        lbl = display_place if not tokens else f"{display_place}\n{bullet * tokens}"
        g.add_node(pydot.Node(
            f"p_{p}", shape="circle", style="filled",
            fillcolor="#eaf1fb", color="#3b6fb5", penwidth="1.8",
            fontsize="12", label=lbl))
    for t in net.transitions:
        is_tau = t.label == cbm.TAU
        tsym = "\u03c4" if is_tau else t.label
        display_transition = t.name.replace("_", "\n")
        lbl = f"{display_transition}\n[{tsym}]"
        g.add_node(pydot.Node(
            f"t_{t.name}", shape="box", style="filled,rounded",
            fillcolor="#f0f0f0" if is_tau else "#fff3d6",
            color="#9a9a9a" if is_tau else "#c9962b", penwidth="1.8",
            fontsize="11", label=lbl))
        for p in t.pre:
            g.add_edge(pydot.Edge(f"p_{p}", f"t_{t.name}", color="#666", penwidth="1.2"))
        for p in t.post:
            g.add_edge(pydot.Edge(f"t_{t.name}", f"p_{p}", color="#666", penwidth="1.2"))
    g.write_pdf(os.path.splitext(path)[0] + ".pdf")
    g.set_dpi("300")
    g.write_png(path)


# ---------------------------------------------------------------------------
# Phase 5 : reachability-graph (LTS) drawing
# ---------------------------------------------------------------------------
def draw_lts(lts: cbm.LTS, path: str, _title: str):
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
    ax.axis("off")
    fig.tight_layout()
    save_artwork(fig, path)
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
    save_artwork(fig, os.path.join(FIG, "fig_pipeline.png"))
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
    fig.tight_layout()
    save_artwork(fig, os.path.join(FIG, "fig_robustness.png"))
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
    ax.legend(frameon=False, fontsize=8, loc="lower right")
    fig.tight_layout()
    save_artwork(fig, os.path.join(FIG, "fig_nullbaseline.png"))
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
            "Every transition is tied to provenance; public GINsim controls and three independent HPN-DREAM model families exercise the pipeline outside case-study curation.",
            "Appendix provenance; public and HPN-DREAM validation CSVs",
        ),
        (
            "All external comparisons are transformed controls without biological data.",
            "Structure-only medoids from three independently inferred public families are fixed without test access, compared formally and scored against held-out mTOR-inhibitor profiles. The nonsignificant specificity result is retained and limits the claim.",
            "hpn_dream_formal_data_validation.csv; hpn_dream_caspots_summary.json; Fig. 8",
        ),
        (
            "The formal verdicts depend on one unverified implementation.",
            "Strong and weak decisions are cross-checked from AUT exports with mCRL2 202607.0; one-way simulation additionally agrees with an independent attacker-defender game on every one- and two-state LTS over a/tau.",
            "mcrl2_synthetic_validation.csv; simulation_oracle_exhaustive.csv",
        ),
        (
            "A deliberately weak structural baseline inflates the apparent advantage.",
            "The benchmark now executes the published 151-graphlet/592-slot PN-GDDA directly on Petri nets, audits it against Holmes, and retains LTS-GDA as a labelled reachable-state comparator.",
            "pn_gdda_catalog_validation.json; pn_gdda_native_modules.csv; pn_gdda_threshold_sensitivity.csv",
        ),
        (
            "The conclusions may be an artefact of asynchronous Boolean updates.",
            "All nine HPN-DREAM comparisons are repeated under a global synchronous stress semantics; seven classes persist and two weaken to non-comparability.",
            "hpn_dream_semantic_sensitivity.csv",
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
            "Claims remain model-level; external tests include a public 826-state cell-cycle LTS while explicitly avoiding biological overclaim.",
            "Public-model table; Discussion and conclusion",
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


# ---------------------------------------------------------------------------
# Independent synthetic benchmark, baselines and runtime scaling
# ---------------------------------------------------------------------------
def fig_method_benchmark():
    rows = mb.validation_benchmark(n_steps=12, seed=17, k=8)
    df = pd.DataFrame(rows)
    df.to_csv(os.path.join(RES, "synthetic_benchmark.csv"), index=False)

    accuracy = pd.DataFrame(mb.baseline_accuracy(rows))
    accuracy.to_csv(os.path.join(RES, "baseline_accuracy.csv"), index=False)
    threshold_sensitivity = pd.DataFrame(mb.pn_gdda_threshold_sensitivity(rows))
    threshold_sensitivity.to_csv(
        os.path.join(RES, "pn_gdda_threshold_sensitivity.csv"), index=False
    )

    native = pd.DataFrame(pn_gdda.native_module_comparisons(k=6))
    native.to_csv(os.path.join(RES, "pn_gdda_native_modules.csv"), index=False)
    with open(os.path.join(RES, "pn_gdda_catalog_validation.json"), "w") as f:
        json.dump(pn_gdda.catalog_validation(), f, indent=2, sort_keys=True)
        f.write("\n")

    formal_labels = {
        "weak equivalence": "weak bisimulation",
        "one-way simulation": "one-way simulation",
        "not comparable": "not comparable",
    }
    with open(os.path.join(RES, "pn_gdda_native_modules.tex"), "w") as f:
        f.write("\\begin{tabular}{lcccl}\n\\toprule\n")
        f.write("Module & PN-GDDA-592 & Orbit-576 & $\\geq0.9$ & Formal relation \\\\\n")
        f.write("\\midrule\n")
        for row in native.to_dict("records"):
            decision = "yes" if row["pn_gdda_equivalent_at_0_9"] else "no"
            f.write(
                f"{row['module']} & {row['pn_gdda_592_similarity']:.4f} & "
                f"{row['pn_gdda_576_similarity']:.4f} & {decision} & "
                f"{formal_labels[row['formal_class']]} \\\\\n"
            )
        f.write("\\bottomrule\n\\end{tabular}\n")

    expected = df["expected_weak_equivalent"].astype(bool).to_numpy()
    methods = [
        ("Weak\nbisimulation", df["weak_bisimilar"].astype(bool).to_numpy()),
        ("Trace\nequality", df["trace_equivalent_at_k"].astype(bool).to_numpy()),
        ("PN-GDDA\n592", df["pn_gdda_equivalent_at_0_9"].astype(bool).to_numpy()),
        ("LTS-GDA", df["lts_gda_equivalent_at_0_9"].astype(bool).to_numpy()),
        ("Structural\nprofile", df["structurally_equivalent_at_0_9"].astype(bool).to_numpy()),
    ]
    correctness = np.column_stack([prediction == expected for _, prediction in methods])

    fig, (ax0, ax1) = plt.subplots(
        1, 2, figsize=(11.2, 4.2), gridspec_kw={"width_ratios": [1.7, 1]}
    )
    ax0.imshow(correctness.astype(int), cmap="RdYlGn", vmin=0, vmax=1, aspect="auto")
    ax0.set_xticks(range(len(methods)))
    ax0.set_xticklabels([name for name, _ in methods], fontsize=8)
    ax0.set_yticks(range(len(df)))
    ax0.set_yticklabels(df["case"], fontsize=8)
    for i in range(correctness.shape[0]):
        for j in range(correctness.shape[1]):
            prediction = methods[j][1][i]
            ax0.text(
                j,
                i,
                "correct" if correctness[i, j] else "error",
                ha="center",
                va="center",
                fontsize=7,
                color="white",
            )
            ax0.text(
                j,
                i + 0.25,
                "equiv." if prediction else "not equiv.",
                ha="center",
                va="center",
                fontsize=6,
                color="white",
            )
    ax0.set_title("Case-level equivalence decisions")
    ax0.set_xlabel("Method")

    colors = [C_PLANT, C_GOLD, "#7a5195", C_HUMAN, C_RED]
    bars = ax1.bar(
        accuracy["method"], accuracy["accuracy"], color=colors, edgecolor="#333333"
    )
    ax1.set_ylim(0, 1.08)
    ax1.set_ylabel("Accuracy against construction ground truth")
    ax1.set_xticks(range(len(accuracy)))
    ax1.set_xticklabels(
        ["Weak\nbisim.", "Trace\nequality", "PN-GDDA\n592", "LTS-GDA", "Structural\nprofile"],
        fontsize=8,
    )
    ax1.set_title("Binary equivalence accuracy")
    for bar, value in zip(bars, accuracy["accuracy"]):
        ax1.text(
            bar.get_x() + bar.get_width() / 2,
            value + 0.025,
            f"{value:.3f}",
            ha="center",
            va="bottom",
            fontsize=8,
        )
    fig.tight_layout()
    save_artwork(fig, os.path.join(FIG, "fig_benchmark_validation.png"))
    plt.close(fig)
    return df, accuracy


def external_validation_tables():
    """Run mCRL2 cross-checks and public-model validation."""
    model_df = pd.DataFrame(pv.public_model_summary())
    model_df.to_csv(os.path.join(RES, "public_models.csv"), index=False)

    public_df = pd.DataFrame(pv.run_public_validation())
    public_df.to_csv(os.path.join(RES, "public_model_validation.csv"), index=False)

    synthetic_df = pd.DataFrame(pv.run_synthetic_mcrl2_validation())
    synthetic_df.to_csv(
        os.path.join(RES, "mcrl2_synthetic_validation.csv"), index=False
    )
    semantics_df = pd.DataFrame(pv.public_semantic_sensitivity())
    semantics_df.to_csv(
        os.path.join(RES, "public_model_semantic_sensitivity.csv"), index=False
    )

    oracle_result = simulation_oracle.exhaustive_simulation_validation(max_states=2)
    oracle_df = pd.DataFrame(
        [{key: value for key, value in oracle_result.items() if key != "counterexamples"}]
    )
    oracle_df.to_csv(
        os.path.join(RES, "simulation_oracle_exhaustive.csv"), index=False
    )
    return model_df, public_df, synthetic_df, semantics_df, oracle_df


def fig_hpn_dream_validation():
    """Blind held-out validation on three public HPN-DREAM model families."""
    hpn.write_results(use_mcrl2=True)
    formal = pd.read_csv(os.path.join(RES, "hpn_dream_formal_data_validation.csv"))
    caspots_path = os.path.join(RES, "hpn_dream_caspots_rmse.csv")
    if not os.path.isfile(caspots_path):
        raise FileNotFoundError(
            "Missing results/hpn_dream_caspots_rmse.csv. Run the pinned "
            "CASPOTS environment command documented in REPRODUCIBILITY.md."
        )
    caspots = pd.read_csv(caspots_path)
    blind = caspots[caspots["selection"] == "blind_structure_medoid"].copy()
    matrix = (
        blind.pivot(index="source_cell", columns="target_cell", values="excess_rmse")
        .reindex(index=hpn.CELLS, columns=hpn.CELLS)
    )
    stats = hpn.concordance_test(formal.to_dict("records"))

    fig, (ax0, ax1) = plt.subplots(1, 2, figsize=(10.4, 4.1))
    vmax = max(0.013, float(matrix.to_numpy().max()))
    image = ax0.imshow(matrix, cmap="YlOrRd", vmin=0, vmax=vmax, aspect="equal")
    ax0.set_xticks(range(len(hpn.CELLS)))
    ax0.set_xticklabels(hpn.CELLS)
    ax0.set_yticks(range(len(hpn.CELLS)))
    ax0.set_yticklabels(hpn.CELLS)
    ax0.set_xlabel("Held-out target cell line")
    ax0.set_ylabel("Blind source-model medoid")
    ax0.set_title("CASPOTS excess RMSE")
    for i, source in enumerate(hpn.CELLS):
        for j, target in enumerate(hpn.CELLS):
            value = matrix.loc[source, target]
            ax0.text(j, i, f"{value:.4f}", ha="center", va="center", fontsize=8)
            if source == target:
                ax0.add_patch(
                    plt.Rectangle(
                        (j - 0.48, i - 0.48), 0.96, 0.96,
                        fill=False, edgecolor="#174a7e", linewidth=2.0,
                    )
                )
    fig.colorbar(image, ax=ax0, fraction=0.046, pad=0.04)

    order = ["one_way_simulation", "not_comparable"]
    labels = ["One-way\nsimulation", "Not\ncomparable"]
    colors = {"mTORi": C_HUMAN, "IGF1+mTORi": C_PLANT, "4EBP1+mTORi": C_GOLD}
    markers = {"mTORi": "o", "IGF1+mTORi": "s", "4EBP1+mTORi": "^"}
    for position, formal_class in enumerate(order):
        subset = formal[formal["formal_class"] == formal_class]
        for condition, group in subset.groupby("condition", sort=False):
            offsets = (
                np.linspace(-0.08, 0.08, len(group))
                if len(group) > 1
                else np.array([0.0])
            )
            ax1.scatter(
                position + offsets,
                group["experimental_rmse"],
                color=colors[condition],
                marker=markers[condition],
                edgecolor="#333333",
                linewidth=0.5,
                s=48,
                label=condition if position == 0 else None,
                zorder=3,
            )
        if len(subset):
            ax1.hlines(
                subset["experimental_rmse"].median(),
                position - 0.18,
                position + 0.18,
                color="#222222",
                linewidth=2,
            )
    ax1.set_xticks(range(len(order)))
    ax1.set_xticklabels(labels)
    ax1.set_ylabel("Between-cell post-zero profile RMSE")
    ax1.set_title("Data distance by formal class")
    ax1.text(
        0.02,
        0.98,
        f"ordinal-class $\\rho$={stats['formal_class_spearman_rho']:.2f}\n"
        f"exact $p$={stats['formal_class_exact_permutation_p_one_sided']:.3f}\n"
        f"LTS-GDA distance $\\rho$={stats['graphlet_distance_spearman_rho']:.2f}\n"
        f"exact $p$={stats['graphlet_distance_exact_permutation_p_one_sided']:.3f}",
        transform=ax1.transAxes,
        ha="left",
        va="top",
        fontsize=8,
    )
    ax1.legend(frameon=False, fontsize=7, loc="lower right")
    fig.tight_layout()
    save_artwork(fig, os.path.join(FIG, "fig_hpn_dream_validation.png"))
    plt.close(fig)
    return formal, blind, stats


def fig_scalability():
    rows = mb.scalability_benchmark(
        sizes=(8, 16, 32, 64, 96, 128), repeats=3, seed=23
    )
    df = pd.DataFrame(rows)
    df.to_csv(os.path.join(RES, "scalability_runtime.csv"), index=False)
    deterministic = df.drop(
        columns=[
            "strong_bisimulation_ms",
            "weak_bisimulation_ms",
            "two_simulations_ms",
            "trace_distance_ms",
            "total_runtime_ms",
        ]
    )
    deterministic.to_csv(os.path.join(RES, "scalability_structure.csv"), index=False)

    fig, (ax0, ax1) = plt.subplots(1, 2, figsize=(9.8, 3.9))
    styles = {
        "identity": (C_HUMAN, "o", "-"),
        "silent refinement": (C_PLANT, "s", "--"),
    }
    for variant, group in df.groupby("variant", sort=False):
        color, marker, line = styles[variant]
        ax0.plot(
            group["candidate_relation_pairs"],
            group["total_runtime_ms"],
            marker=marker,
            linestyle=line,
            color=color,
            linewidth=1.7,
            markersize=5,
            label=variant,
        )
    ax0.set_xscale("log")
    ax0.set_yscale("log")
    ax0.set_xlabel("Candidate state pairs $|S_1| |S_2|$")
    ax0.set_ylabel("Median total runtime (ms)")
    ax0.set_title("Observed runtime scaling")
    ax0.legend(frameon=False, fontsize=8)

    largest = df[df["n_steps"] == df["n_steps"].max()].copy()
    components = [
        "strong_bisimulation_ms",
        "weak_bisimulation_ms",
        "two_simulations_ms",
        "trace_distance_ms",
    ]
    labels = ["Strong bisim.", "Weak bisim.", "Two simulations", "Trace distance"]
    bottom = np.zeros(len(largest))
    component_colors = ["#4c78a8", "#2b8a3e", "#d69e2e", "#c94f4f"]
    for component, label, color in zip(components, labels, component_colors):
        values = largest[component].to_numpy()
        ax1.bar(largest["variant"], values, bottom=bottom, label=label, color=color)
        bottom += values
    ax1.set_ylabel("Median runtime at 128 steps (ms)")
    ax1.set_title("Runtime decomposition")
    ax1.tick_params(axis="x", labelrotation=12, labelsize=8)
    ax1.legend(frameon=False, fontsize=7)
    fig.tight_layout()
    save_artwork(fig, os.path.join(FIG, "fig_scalability.png"))
    plt.close(fig)
    return df


def export_netmahib_artwork() -> None:
    """Create submission-facing vector filenames in citation order."""
    aliases = {
        "Fig1.pdf": "fig_pipeline.pdf",
        "Fig2a.pdf": "fig_ddr_petri_animal.pdf",
        "Fig2b.pdf": "fig_ddr_petri_plant.pdf",
        "Fig3.pdf": "fig_benchmark_validation.pdf",
        "Fig4.pdf": "fig_scalability.pdf",
        "Fig5a.pdf": "fig_ddr_lts_animal.pdf",
        "Fig5b.pdf": "fig_ddr_lts_plant.pdf",
        "Fig6a.pdf": "fig_rcd_petri_animal.pdf",
        "Fig6b.pdf": "fig_rcd_petri_plant.pdf",
        "Fig7a.pdf": "fig_robustness.pdf",
        "Fig7b.pdf": "fig_nullbaseline.pdf",
        "Fig8.pdf": "fig_hpn_dream_validation.pdf",
    }
    for target, source in aliases.items():
        shutil.copy2(os.path.join(FIG, source), os.path.join(FIG, target))


def main():
    print(">> Independent method benchmark")
    benchmark_df, accuracy_df = fig_method_benchmark()
    print(">> mCRL2 and public-model validation")
    (
        public_models_df,
        public_validation_df,
        mcrl2_synthetic_df,
        public_semantics_df,
        simulation_oracle_df,
    ) = external_validation_tables()
    print(">> Blind HPN-DREAM held-out validation")
    hpn_formal_df, hpn_caspots_df, hpn_stats = fig_hpn_dream_validation()
    print(">> Scalability benchmark")
    scalability_df = fig_scalability()
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
    print(">> NetMAHIB vector artwork")
    export_netmahib_artwork()

    print("\n== Comparability summary ==")
    print(df[["module", "strong_bisimilar", "weak_bisimilar",
              "plant_simulated_by_animal", "animal_simulated_by_plant",
              "distance", "verdict"]].to_string(index=False))
    print("\n== Null baseline ==")
    print(nb_df.to_string(index=False))
    print("\n== Cross-organism generalisation (cell cycle vs Human) ==")
    print(gen_df[["organism", "strong_bisimilar", "weak_bisimilar",
                  "distance", "verdict"]].to_string(index=False))
    print("\n== Synthetic benchmark ==")
    print(benchmark_df[["case", "expected_class", "formal_class", "formal_match"]].to_string(index=False))
    print("\n== Baseline accuracy ==")
    print(accuracy_df[["method", "accuracy", "false_positive", "false_negative"]].to_string(index=False))
    print("\n== Public models ==")
    print(public_models_df[[
        "model", "variables", "reachable_states", "reachable_edges"
    ]].to_string(index=False))
    print("\n== Independent-oracle agreement ==")
    print(
        "Synthetic strong/weak decisions:",
        int(mcrl2_synthetic_df["python_mcrl2_strong_agree"].sum())
        + int(mcrl2_synthetic_df["python_mcrl2_weak_agree"].sum()),
        "/",
        2 * len(mcrl2_synthetic_df),
    )
    print(
        "Public controls fully matching expectations:",
        int(public_validation_df["all_expected_results_match"].sum()),
        "/",
        len(public_validation_df),
    )
    print("Exhaustive simulation-game oracle:")
    print(simulation_oracle_df.to_string(index=False))
    print("\n== Public-model semantic sensitivity ==")
    print(public_semantics_df.to_string(index=False))
    print("\n== HPN-DREAM held-out validation ==")
    print(hpn_formal_df[[
        "condition", "left_cell", "right_cell", "formal_class",
        "experimental_rmse", "trace_distance_k6"
    ]].to_string(index=False))
    print("Class/data exact test:", hpn_stats)
    print("Blind CASPOTS scores:")
    print(hpn_caspots_df[[
        "source_cell", "target_cell", "native_context", "model_rmse", "excess_rmse"
    ]].to_string(index=False))
    print("\n== Largest scalability cases ==")
    print(scalability_df[scalability_df["n_steps"] == scalability_df["n_steps"].max()][[
        "variant", "n_states_reference", "n_states_candidate", "total_runtime_ms"
    ]].to_string(index=False))
    print(f"\nFigures -> {FIG}\nResults -> {RES}")


if __name__ == "__main__":
    main()
