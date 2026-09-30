"""Compare the audit outputs in results/audit/ with the values printed in the paper.

    python src/compare_to_paper.py
"""
import csv
import os
import sys

from corpora import ROOT

AUD = os.path.join(os.environ.get("RESULTS_DIR", os.path.join(ROOT, "results")), "audit")


def rows(name):
    path = os.path.join(AUD, name)
    if not os.path.exists(path):
        return None
    with open(path) as f:
        return list(csv.reader(f))


def lookup(name, key_cols, key, col):
    r = rows(name)
    if r is None:
        return None
    header, body = r[0], r[1:]
    for line in body:
        if [line[header.index(k)] for k in key_cols] == key:
            return line[header.index(col)]
    return None


def n_lines(name):
    r = rows(name)
    return None if r is None else len(r) - 1


def pid(corpus, col):
    r = rows("patient_leakage.csv")
    if r is None:
        return None
    header = r[1]
    for line in r[2:]:
        if line[0] == corpus:
            return line[header.index(col)]


def figshare(idx):
    r = rows("patient_leakage.csv")
    return None if r is None else r[0][idx]


# (claim, paper value, reproduced value as a string or None, tolerance for numeric comparison)
def checks():
    L, S, X = "leakage_within_corpus.csv", "ncc_sweep.csv", "overlap_across_corpora.csv"
    C = "patient_leakage_by_class.csv"
    return [
        ("Nickparvar train / test images", "5600 / 1600",
         f"{lookup(L, ['corpus'], ['Nickparvar'], 'n_train')} / {lookup(L, ['corpus'], ['Nickparvar'], 'n_test')}", None),
        ("Nickparvar test, exact (MD5) twin in train", "0", lookup(L, ["corpus"], ["Nickparvar"], "exact_md5"), 0),
        ("Nickparvar test, near twin (NCC >= 0.98)", "460", lookup(L, ["corpus"], ["Nickparvar"], "near_ncc098"), 0),
        ("Nickparvar test leak rate, %", "28.75", lookup(L, ["corpus"], ["Nickparvar"], "near_pct"), 0.005),
        ("Nickparvar test flagged at NCC >= 0.995", "432", lookup(S, ["corpus", "threshold"], ["Nickparvar", "0.995"], "n_test_flagged"), 0),
        ("Nickparvar median best-match NCC", "0.919", lookup("best_match_median.csv", ["corpus"], ["Nickparvar"], "median_best_ncc"), 0.0005),
        ("SARTAJ train / test images", "2870 / 394",
         f"{lookup(L, ['corpus'], ['SARTAJ'], 'n_train')} / {lookup(L, ['corpus'], ['SARTAJ'], 'n_test')}", None),
        ("SARTAJ test, byte-identical in train", "88", lookup(L, ["corpus"], ["SARTAJ"], "exact_md5"), 0),
        ("SARTAJ test, byte-identical, %", "22.34", lookup(L, ["corpus"], ["SARTAJ"], "exact_pct"), 0.005),
        ("SARTAJ test, near twin, %", "65.74", lookup(L, ["corpus"], ["SARTAJ"], "near_pct"), 0.005),
        ("Kermany control test, exact / near twins", "0 / 0",
         f"{lookup(L, ['corpus'], ['Kermany CXR'], 'exact_md5')} / {lookup(L, ['corpus'], ['Kermany CXR'], 'near_ncc098')}", None),
        ("Kermany control median best-match NCC", "0.900", lookup("best_match_median.csv", ["corpus"], ["Kermany CXR"], "median_best_ncc"), 0.0005),
        ("dHash radius 5 flags Nickparvar test, %", "63", lookup("dhash_radius5.csv", ["corpus"], ["Nickparvar"], "flagged_pct"), 0.5),
        ("dHash radius 5 flags Kermany test, %", "93", lookup("dhash_radius5.csv", ["corpus"], ["Kermany CXR"], "flagged_pct"), 0.5),
        ("SARTAJ in Nickparvar, exact", "2670 (81.8%)",
         f"{lookup(X, ['query', 'reference'], ['sartaj_all', 'nickparvar_all'], 'exact_md5')} ({lookup(X, ['query', 'reference'], ['sartaj_all', 'nickparvar_all'], 'exact_pct')}%)", None),
        ("SARTAJ in Nickparvar, near", "2705 (82.87%)",
         f"{lookup(X, ['query', 'reference'], ['sartaj_all', 'nickparvar_all'], 'near_ncc098')} ({lookup(X, ['query', 'reference'], ['sartaj_all', 'nickparvar_all'], 'near_pct')}%)", None),
        ("Navoneel in Nickparvar, exact / near", "66 / 123 (48.62%)",
         f"{lookup(X, ['query', 'reference'], ['navoneel', 'nickparvar_all'], 'exact_md5')} / {lookup(X, ['query', 'reference'], ['navoneel', 'nickparvar_all'], 'near_ncc098')} ({lookup(X, ['query', 'reference'], ['navoneel', 'nickparvar_all'], 'near_pct')}%)", None),
        ("Navoneel in SARTAJ, exact / near", "0 / 98 (38.74%)",
         f"{lookup(X, ['query', 'reference'], ['navoneel', 'sartaj_all'], 'exact_md5')} / {lookup(X, ['query', 'reference'], ['navoneel', 'sartaj_all'], 'near_ncc098')} ({lookup(X, ['query', 'reference'], ['navoneel', 'sartaj_all'], 'near_pct')}%)", None),
        ("Nickparvar deduplicated test images", "1140", n_lines("lists/nickparvar_test_dedup.csv"), 0),
        ("SARTAJ images left after removing overlap", "559", n_lines("lists/sartaj_clean.csv"), 0),
        ("Navoneel images left after removing overlap", "130", n_lines("lists/navoneel_clean.csv"), 0),
        ("figshare slices / patients", "3064 / 233", None if figshare(1) is None else f"{figshare(1)} / {figshare(3)}", None),
        ("Nickparvar test traceable to figshare", "201 (12.56%)",
         None if pid("Nickparvar", "traceable") is None else f"{pid('Nickparvar', 'traceable')} ({pid('Nickparvar', 'traceable_pct')}%)", None),
        ("Nickparvar traceable test patients", "125", pid("Nickparvar", "patients"), 0),
        ("Nickparvar traceable test with same patient in train", "192 (95.52%)",
         None if pid("Nickparvar", "same_patient_in_train") is None else f"{pid('Nickparvar', 'same_patient_in_train')} ({pid('Nickparvar', 'same_patient_pct_of_traceable')}%)", None),
        ("SARTAJ test traceable / same patient in train", "28 (7.11%) / 28 (100.0%)",
         None if pid("SARTAJ", "traceable") is None else f"{pid('SARTAJ', 'traceable')} ({pid('SARTAJ', 'traceable_pct')}%) / {pid('SARTAJ', 'same_patient_in_train')} ({pid('SARTAJ', 'same_patient_pct_of_traceable')}%)", None),
        ("Traceable / leaked by class (glioma, meningioma, notumor, pituitary)", "98/90, 26/26, 0/0, 77/76",
         None if rows(C) is None else ", ".join(f"{r[2]}/{r[3]}" for r in rows(C)[1:]), None),
    ]


def main():
    print(f"{'claim':70s} | {'paper':26s} | {'reproduced':26s} | match")
    print("-" * 140)
    n_run = n_ok = 0
    for claim, paper, got, tol in checks():
        if got is None or "None" in str(got):
            status, got = "not run", "-"
        else:
            n_run += 1
            if tol is None:
                ok = got == paper
            else:
                ok = abs(float(got) - float(paper)) <= tol
            n_ok += ok
            status = "yes" if ok else "no"
        print(f"{claim:70s} | {paper:26s} | {str(got):26s} | {status}")
    print(f"\n{n_ok}/{n_run} values match the paper.")
    if n_ok < n_run:
        sys.exit(1)


if __name__ == "__main__":
    main()
