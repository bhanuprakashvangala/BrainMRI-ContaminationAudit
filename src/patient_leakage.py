"""Patient-layer audit (Tables III and IV, Fig. 4 of the paper), CPU only.

The figshare release of Cheng et al. (https://doi.org/10.6084/m9.figshare.1512427) stores a patient
key, cjdata.PID, with every slice. Each Kaggle image is matched to its figshare original with the NCC
criterion (rho >= 0.98) and inherits that key. A traceable test image is leaked when a training
image of the same corpus carries the same patient key.

The figshare arrays are column-major; they must be transposed after reading with h5py, otherwise
nothing matches.

Needs the figshare .mat files: python data/download.py --figshare
Writes results/audit/patient_leakage*.csv and results/audit/lists/*_patient_ids.csv.
Run: python src/patient_leakage.py
"""
import csv
import os

import h5py
import numpy as np
from PIL import Image

from corpora import ROOT, label_of, split
from imaging import SIDE, best_match, ncc_vectors, rel

OUT = os.path.join(os.environ.get("RESULTS_DIR", os.path.join(ROOT, "results")), "audit")
FIGSHARE_DIR = os.environ.get("FIGSHARE_DIR", os.path.join(ROOT, "data", "figshare"))
TAU = 0.98


def load_figshare():
    files = sorted((f for f in os.listdir(FIGSHARE_DIR) if f.endswith(".mat")), key=lambda f: int(f[:-4]))
    if not files:
        raise SystemExit(f"no .mat files in {FIGSHARE_DIR}: run `python data/download.py --figshare`")
    V = np.zeros((len(files), SIDE * SIDE), np.float32)
    pids = []
    for i, name in enumerate(files):
        with h5py.File(os.path.join(FIGSHARE_DIR, name), "r") as f:
            c = f["cjdata"]
            img = np.array(c["image"], np.float32).T  # column-major on disk
            pids.append("".join(chr(int(x)) for x in np.array(c["PID"]).ravel()))
        img = (img - img.min()) / max(float(img.max() - img.min()), 1e-6) * 255.0
        a = np.asarray(Image.fromarray(img.astype(np.uint8)).resize((SIDE, SIDE), Image.LANCZOS), np.float32).ravel()
        a -= a.mean()
        V[i] = a / np.linalg.norm(a)
    return V, np.array(pids)


def trace(paths, Vfig, pids):
    """Patient key of each image (None when it has no figshare original at rho >= TAU)."""
    best, arg = best_match(ncc_vectors(paths), Vfig)
    return [pids[j] if b >= TAU else None for b, j in zip(best, arg)], best


def main():
    os.makedirs(os.path.join(OUT, "lists"), exist_ok=True)
    Vfig, pids = load_figshare()
    n_pat = len(set(pids))
    print(f"figshare: {len(pids)} slices from {n_pat} patients ({len(pids) / n_pat:.1f} per patient)")
    summary, per_class = [], []
    for corpus, label in [("nickparvar", "Nickparvar"), ("sartaj", "SARTAJ")]:
        base, tr = split(corpus, "train")
        _, te = split(corpus, "test")
        pid_tr, _ = trace(tr, Vfig, pids)
        pid_te, best_te = trace(te, Vfig, pids)
        train_pids = {p for p in pid_tr if p is not None}
        traceable = [p is not None for p in pid_te]
        leaked = [p is not None and p in train_pids for p in pid_te]
        n, k, m = len(te), sum(traceable), sum(leaked)
        n_patients = len({p for p in pid_te if p is not None})
        summary.append([label, n, k, round(100 * k / n, 2), n_patients, m, round(100 * m / max(k, 1), 2)])
        if corpus == "nickparvar":
            labels = [label_of(p) for p in te]
            for c in sorted(set(labels)):
                idx = [i for i, l in enumerate(labels) if l == c]
                per_class.append([c, len(idx), sum(traceable[i] for i in idx), sum(leaked[i] for i in idx)])
        with open(os.path.join(OUT, "lists", f"{corpus}_patient_ids.csv"), "w", newline="") as f:
            w = csv.writer(f, lineterminator="\n")
            w.writerow(["split", "path", "figshare_pid", "ncc"])
            for p, pid in zip(tr, pid_tr):
                if pid is not None:
                    w.writerow(["train", rel(p, base), pid, ""])
            for p, pid, b in zip(te, pid_te, best_te):
                if pid is not None:
                    w.writerow(["test", rel(p, base), pid, f"{b:.4f}"])

    with open(os.path.join(OUT, "patient_leakage.csv"), "w", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["figshare_slices", len(pids), "figshare_patients", n_pat, "", "", ""])
        w.writerow(["corpus", "n_test", "traceable", "traceable_pct", "patients", "same_patient_in_train",
                    "same_patient_pct_of_traceable"])
        w.writerows(summary)
    with open(os.path.join(OUT, "patient_leakage_by_class.csv"), "w", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["class", "n", "traceable", "same_patient_in_train"])
        w.writerows(per_class)
    for r in summary:
        print(r)
    for r in per_class:
        print(r)


if __name__ == "__main__":
    main()
