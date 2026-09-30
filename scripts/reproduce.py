"""Run the CPU audits and compare them with the paper.

    python scripts/reproduce.py              # download data, duplicate audit, figures
    python scripts/reproduce.py --patients   # also download figshare (~880 MB) and run the patient audit

Takes about 15 minutes on a laptop CPU, plus download time.
"""
import argparse
import os
import subprocess
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def run(*args):
    print(f"\n$ python {' '.join(args)}", flush=True)
    subprocess.run([sys.executable, *args], check=True, cwd=ROOT)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--patients", action="store_true", help="also run the figshare patient-ID audit")
    args = ap.parse_args()
    run("data/download.py", *(["--figshare"] if args.patients else []))
    run("src/audit_duplicates.py")
    if args.patients:
        run("src/patient_leakage.py")
    run("src/make_figures.py")
    run("src/compare_to_paper.py")


if __name__ == "__main__":
    main()
