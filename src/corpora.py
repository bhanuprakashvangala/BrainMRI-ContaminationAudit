"""Where the corpora live and how their official splits and labels are read.

data/download.py writes data/paths.json with the local folder of each Kaggle dataset.
"""
import json
import os

from imaging import list_images

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PATHS_FILE = os.path.join(ROOT, "data", "paths.json")


def roots():
    if not os.path.exists(PATHS_FILE):
        raise SystemExit("data/paths.json not found: run `python data/download.py` first")
    with open(PATHS_FILE) as f:
        return json.load(f)


def split(corpus, name):
    """(root, list of image paths) for a corpus split.

    corpus: nickparvar | sartaj | navoneel | kermany ; name: train | test | all
    """
    r = roots()
    if corpus == "nickparvar":
        base, sub = r["nickparvar"], {"train": "Training", "test": "Testing"}
    elif corpus == "sartaj":
        base, sub = r["sartaj"], {"train": "Training", "test": "Testing"}
    elif corpus == "kermany":
        base, sub = os.path.join(r["kermany"], "chest_xray"), {"train": "train", "test": "test"}
    elif corpus == "navoneel":
        base = os.path.join(r["navoneel"], "brain_tumor_dataset")
        return base, list_images(base)
    else:
        raise ValueError(corpus)
    if name == "all":
        return base, list_images(os.path.join(base, sub["train"])) + list_images(os.path.join(base, sub["test"]))
    return base, list_images(os.path.join(base, sub[name]))


def label_of(path):
    """Class label = name of the image's parent folder."""
    return os.path.basename(os.path.dirname(path))
