"""Journal GIM artwork, with values taken from regenerated result CSVs."""
from pathlib import Path
import csv
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "Journal"
TEAL, GREEN, RED, INK = "#176c88", "#31754d", "#a64247", "#222222"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10, "pdf.fonttype": 42})


def box(ax, x, y, w, h, text, color=TEAL, fontsize=10, face="white"):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.007,rounding_size=0.006",
                               facecolor=face, edgecolor=color, linewidth=1.2))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fontsize, color=INK)


def arrow(ax, start, end, color="#666666"):
    ax.annotate("", xy=end, xytext=start,
                arrowprops={"arrowstyle": "->", "color": color, "lw": 1.2, "shrinkA": 2, "shrinkB": 2})


def save(fig, name):
    fig.savefig(OUT / (name + ".pdf"), bbox_inches="tight", metadata={"CreationDate": None, "ModDate": None})
    fig.savefig(OUT / (name + ".png"), bbox_inches="tight", dpi=180)
    plt.close(fig)


def gim():
    with (ROOT / "results/gim_interface_sensitivity.csv").open() as handle:
        rows = list(csv.DictReader(handle))
    fig, ax = plt.subplots(figsize=(7.2, 7.6))
    ax.set(xlim=(0, 1), ylim=(0, 1)); ax.axis("off")
    ax.text(.01, .985, "(a) Encoded biological functions and mechanisms", fontsize=12, fontweight="bold", va="top")
    for x, label in zip([.1175, .3575, .61, .87], ["Detect", "Checkpoint", "Repair /\nrecover", "Terminal\nresponse"]):
        ax.text(x, .916, label, ha="center", fontsize=9.1, fontweight="bold")
    ax.text(.02, .864, "Animal / human", color=TEAL, fontweight="bold")
    ax.text(.02, .660, r"$\it{Arabidopsis}$", color=GREEN, fontweight="bold")
    xs, widths = [.025, .265, .505, .765], [.185, .185, .21, .21]
    animal = ["ATM / ATR\ndamage channels", "CHK1/2\np53-p21", "HR/NHEJ\nBER/NER", "Apoptosis"]
    plant = ["ATM / ATR\ndamage channels", "SOG1-WEE1\nSMR checkpoint", "HR/NHEJ\nExcision repair", "SMR induction\nthen differentiation /\nendoreduplication*"]
    for y, texts, color in [(.730, animal, TEAL), (.514, plant, GREEN)]:
        for i, (x, w, label) in enumerate(zip(xs, widths, texts)):
            box(ax, x, y, w, .106, label, color=color, fontsize=7.8 if i == 3 else 8.5,
                face="#fff4f3" if i == 3 else "#f7faf9")
    ax.text(.02, .481, "*One combined terminal transition in the plant encoding, not two alternatives.", fontsize=8.2, va="top")
    ax.text(.01, .425, "(b) Same structures, different observational resolution", fontsize=12, fontweight="bold")
    for x, label in [(.02, "Readout"), (.20, "What is distinguished"), (.63, "PN-GDDA"), (.80, "Branching relation")]:
        ax.text(x, .376, label, fontsize=8.8, fontweight="bold")
    descriptions = ["Shared functions; terminal\nloss of proliferative capacity",
                    "Damage, ATM/ATR and repair;\nterminal mechanisms collapsed",
                    "Pathway events plus separate\nanimal / plant terminal mechanisms"]
    names = ["A  Coarse", "B  Pathway", "C  Terminal"]
    for i, (row, description, name) in enumerate(zip(rows, descriptions, names)):
        y = .295 - .102*i
        ax.axhspan(y-.034, y+.052, xmin=.01, xmax=.99, color="#edf5f1" if row["weak_bisimulation"] == "True" else "#fbebeb", zorder=0)
        relation = "Weakly\nbisimilar" if row["weak_bisimulation"] == "True" else "Non-comparable\n(both directions fail)"
        ax.text(.02, y+.012, name, fontsize=9.2, va="center", fontweight="bold")
        ax.text(.20, y+.012, description, fontsize=8.7, va="center")
        ax.text(.68, y+.012, f'{float(row["pn_gdda_592_similarity"]):.4f}', fontsize=10, ha="center", va="center")
        ax.text(.885, y+.012, relation, fontsize=8.3, ha="center", va="center", color=GREEN if i<2 else RED)
    ax.text(.5, .017, "Model- and interface-conditional results; no organism-level equivalence", ha="center", fontsize=8.9, color="#555555")
    save(fig, "Fig2")


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    gim()
    print("Generated Journal/Fig2 from the interface results.")
