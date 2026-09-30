"""Download the public corpora audited in the paper with kagglehub and record where they are.

    pip install kagglehub
    python data/download.py              # the four Kaggle corpora
    python data/download.py --figshare   # also the figshare release used for patient IDs (~880 MB)

Public Kaggle datasets can usually be fetched without an account; if Kaggle asks for credentials,
set KAGGLE_USERNAME and KAGGLE_KEY (see https://github.com/Kaggle/kagglehub). The images stay in the
kagglehub cache (about 2.6 GB in total); only data/paths.json is written here.
"""
import argparse
import json
import os
import urllib.request
import zipfile

import kagglehub

HERE = os.path.dirname(os.path.abspath(__file__))

DATASETS = {
    # C1, 7,200 images in four classes, official Training/Testing = 5,600/1,600
    "nickparvar": "masoudnickparvar/brain-tumor-mri-dataset/versions/2",
    # C2, 3,264 images in four classes, official Training/Testing = 2,870/394
    "sartaj": "sartajbhuvaji/brain-tumor-classification-mri/versions/3",
    # C3, 253 images, yes/no
    "navoneel": "navoneel/brain-mri-images-for-brain-tumor-detection/versions/1",
    # negative control: Kermany pediatric chest X-ray, train/test = 5,216/624
    "kermany": "paultimothymooney/chest-xray-pneumonia/versions/2",
}


# Cheng et al., figshare article 1512427 (CC BY 4.0): 3,064 .mat slices with cjdata.PID
FIGSHARE_FILES = [3381290, 3381296, 3381293, 3381302]


def download_figshare():
    out = os.path.join(HERE, "figshare")
    os.makedirs(out, exist_ok=True)
    for fid in FIGSHARE_FILES:
        zpath = os.path.join(out, f"{fid}.zip")
        if not os.path.exists(zpath):
            print(f"downloading figshare file {fid}", flush=True)
            urllib.request.urlretrieve(f"https://ndownloader.figshare.com/files/{fid}", zpath)
        with zipfile.ZipFile(zpath) as z:
            z.extractall(out)
    n = len([f for f in os.listdir(out) if f.endswith(".mat")])
    print(f"figshare: {n} .mat files in data/figshare")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--figshare", action="store_true", help="also download the figshare release")
    args = ap.parse_args()
    paths = {}
    for key, handle in DATASETS.items():
        paths[key] = kagglehub.dataset_download(handle)
        print(f"{key:11s} {handle} -> {paths[key]}", flush=True)
    with open(os.path.join(HERE, "paths.json"), "w") as f:
        json.dump(paths, f, indent=1)
    print("wrote data/paths.json")
    if args.figshare:
        download_figshare()


if __name__ == "__main__":
    main()
