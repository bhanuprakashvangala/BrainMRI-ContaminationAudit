"""Plot the audit results (counterparts of Figs. 1, 3 and 4 of the paper) from results/audit/.

    python src/make_figures.py
"""
import csv
import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

from corpora import ROOT  # noqa: E402

RES = os.environ.get("RESULTS_DIR", os.path.join(ROOT, "results"))
AUD, FIG = os.path.join(RES, "audit"), os.path.join(RES, "figures")
plt.rcParams.update({"font.size": 8, "axes.spines.top": False, "axes.spines.right": False})


def read(name):
    with open(os.path.join(AUD, name)) as f:
        return list(csv.DictReader(f))


def ncc_sweep():
    rows = [r for r in read("ncc_sweep.csv") if r["corpus"] == "Nickparvar"]
    t = [float(r["threshold"]) for r in rows]
    n = [int(r["n_test_flagged"]) for r in rows]
    fig, ax = plt.subplots(figsize=(3.4, 2.2))
    ax.plot(t, n, "o-", color="#1f5f9e")
    ax.axvline(0.98, color="k", ls="--", lw=0.7)
    for x, y in zip(t, n):
        ax.annotate(str(y), (x, y), textcoords="offset points", xytext=(0, 5), ha="center", fontsize=7)
    ax.set_xlabel("NCC threshold")
    ax.set_ylabel("Nickparvar test images flagged")
    fig.tight_layout()
    fig.savefig(os.path.join(FIG, "ncc_sweep.pdf"))
    plt.close(fig)


def best_match_distribution():
    fig, ax = plt.subplots(figsize=(3.4, 2.2))
    bins = np.linspace(0.6, 1.0, 81)
    for name, label, col in [("nickparvar", "Nickparvar (brain MRI)", "#c0392b"), ("kermany", "Kermany (chest X-ray control)", "#7f8c8d")]:
        f = os.path.join(AUD, f"{name}_test_best_ncc.npy")
        if os.path.exists(f):
            ax.hist(np.load(f), bins=bins, histtype="step", lw=1.2, color=col, label=label, density=True)
    ax.axvline(0.98, color="k", ls="--", lw=0.7)
    ax.set_xlabel("best-match NCC against the training split")
    ax.set_ylabel("density")
    ax.legend(frameon=False, fontsize=6.5, loc="upper left")
    fig.tight_layout()
    fig.savefig(os.path.join(FIG, "best_match_distribution.pdf"))
    plt.close(fig)


def patient_leakage():
    if not os.path.exists(os.path.join(AUD, "patient_leakage_by_class.csv")):
        return
    rows = read("patient_leakage_by_class.csv")
    x = np.arange(len(rows))
    fig, ax = plt.subplots(figsize=(3.4, 2.2))
    ax.bar(x - 0.2, [int(r["traceable"]) for r in rows], 0.4, color="#bdc3c7", label="traceable to figshare")
    ax.bar(x + 0.2, [int(r["same_patient_in_train"]) for r in rows], 0.4, color="#c0392b", label="same patient in train")
    ax.set_xticks(x)
    ax.set_xticklabels([r["class"] for r in rows])
    ax.set_ylabel("Nickparvar test images")
    ax.legend(frameon=False, fontsize=6.5)
    fig.tight_layout()
    fig.savefig(os.path.join(FIG, "patient_leakage_by_class.pdf"))
    plt.close(fig)


if __name__ == "__main__":
    os.makedirs(FIG, exist_ok=True)
    ncc_sweep()
    best_match_distribution()
    patient_leakage()
    print("figures written to", FIG)
