"""Duplicate-layer audit (Tables I and II, Figs. 1 and 3 of the paper), CPU only.

  * within each corpus: official test images with an exact (MD5) or near (NCC >= 0.98) twin in
    the same corpus' official training split, for Nickparvar, SARTAJ and the Kermany control;
  * threshold sweep and best-match medians for Nickparvar and the control;
  * containment across corpora (SARTAJ in Nickparvar, Navoneel in Nickparvar and in SARTAJ);
  * the perceptual-hash check the paper rejects (64-bit difference hash, Hamming radius 5);
  * file lists: leaked test images, the deduplicated Nickparvar test split, and the cleaned
    external SARTAJ and Navoneel sets.

Writes results/audit/*.csv and results/audit/lists/*.csv.   Run: python src/audit_duplicates.py
"""
import csv
import os
import time

import numpy as np

from corpora import ROOT, label_of, split
from imaging import best_match, dhash_bits, md5, min_hamming, ncc_vectors, rel

OUT = os.path.join(os.environ.get("RESULTS_DIR", os.path.join(ROOT, "results")), "audit")
LISTS = os.path.join(OUT, "lists")
TAU = 0.98
SWEEP = [0.90, 0.95, 0.98, 0.99, 0.995]

_cache = {}


def load(corpus, name):
    key = (corpus, name)
    if key not in _cache:
        base, paths = split(corpus, name)
        t = time.time()
        _cache[key] = dict(base=base, paths=paths, md5=[md5(p) for p in paths], V=ncc_vectors(paths))
        print(f"  {corpus}/{name}: {len(paths)} images ({time.time() - t:.0f}s)", flush=True)
    return _cache[key]


def compare(q, r):
    """Exact and best-NCC matches of every query image against the reference set."""
    ref_md5 = set(r["md5"])
    exact = np.array([h in ref_md5 for h in q["md5"]])
    best, arg = best_match(q["V"], r["V"])
    return exact, best, arg


def pct(k, n):
    return round(100.0 * k / n, 2)


def write_csv(path, header, rows):
    with open(path, "w", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(header)
        w.writerows(rows)


def write_list(name, q, r, mask, best, arg):
    rows = [(rel(q["paths"][i], q["base"]), label_of(q["paths"][i]),
             rel(r["paths"][arg[i]], r["base"]) if r is not None else "", f"{best[i]:.4f}")
            for i in np.where(mask)[0]]
    write_csv(os.path.join(LISTS, name), ["path", "label", "best_match", "ncc"], rows)
    return len(rows)


def main():
    os.makedirs(LISTS, exist_ok=True)
    print("loading and hashing images", flush=True)

    # ---- Table I: within-corpus leakage across the official partition
    leak_rows, sweep_rows, dist_rows, dhash_rows = [], [], [], []
    for corpus, label in [("nickparvar", "Nickparvar"), ("sartaj", "SARTAJ"), ("kermany", "Kermany CXR")]:
        tr, te = load(corpus, "train"), load(corpus, "test")
        exact, best, arg = compare(te, tr)
        near = best >= TAU
        n = len(te["paths"])
        leak_rows.append([label, len(tr["paths"]), n, int(exact.sum()), pct(exact.sum(), n),
                          int(near.sum()), pct(near.sum(), n)])
        sweep_rows += [[label, t, int((best >= t).sum())] for t in SWEEP]
        dist_rows.append([label, round(float(np.median(best)), 3)])
        write_list(f"{corpus}_test_leaked.csv", te, tr, near, best, arg)
        if corpus in ("nickparvar", "kermany"):
            ham = min_hamming(dhash_bits(te["paths"]), dhash_bits(tr["paths"]))
            dhash_rows.append([label, n, int((ham <= 5).sum()), pct((ham <= 5).sum(), n)])
        if corpus == "nickparvar":
            write_list("nickparvar_test_dedup.csv", te, tr, ~near, best, arg)
            np.save(os.path.join(OUT, "nickparvar_test_best_ncc.npy"), best)
        if corpus == "kermany":
            np.save(os.path.join(OUT, "kermany_test_best_ncc.npy"), best)
    write_csv(os.path.join(OUT, "leakage_within_corpus.csv"),
              ["corpus", "n_train", "n_test", "exact_md5", "exact_pct", "near_ncc098", "near_pct"], leak_rows)
    write_csv(os.path.join(OUT, "ncc_sweep.csv"), ["corpus", "threshold", "n_test_flagged"], sweep_rows)
    write_csv(os.path.join(OUT, "best_match_median.csv"), ["corpus", "median_best_ncc"], dist_rows)
    write_csv(os.path.join(OUT, "dhash_radius5.csv"), ["corpus", "n_test", "flagged", "flagged_pct"], dhash_rows)

    # ---- Table II: containment across corpora
    nick_all, sar_all, navo = load("nickparvar", "all"), load("sartaj", "all"), load("navoneel", "all")
    cross_rows = []
    for qn, q, rn, r, clean_name in [("sartaj_all", sar_all, "nickparvar_all", nick_all, "sartaj_clean.csv"),
                                     ("navoneel", navo, "nickparvar_all", nick_all, "navoneel_clean.csv"),
                                     ("navoneel", navo, "sartaj_all", sar_all, None)]:
        exact, best, arg = compare(q, r)
        near = best >= TAU
        n = len(q["paths"])
        cross_rows.append([qn, rn, n, int(exact.sum()), pct(exact.sum(), n), int(near.sum()), pct(near.sum(), n)])
        write_list(f"{qn}_in_{rn}.csv", q, r, near, best, arg)
        if clean_name:
            write_list(clean_name, q, r, ~near, best, arg)
    write_csv(os.path.join(OUT, "overlap_across_corpora.csv"),
              ["query", "reference", "n", "exact_md5", "exact_pct", "near_ncc098", "near_pct"], cross_rows)

    for name in ["leakage_within_corpus", "ncc_sweep", "best_match_median", "dhash_radius5", "overlap_across_corpora"]:
        print(f"\n{name}.csv")
        with open(os.path.join(OUT, f"{name}.csv")) as f:
            print(f.read().strip())


if __name__ == "__main__":
    main()
