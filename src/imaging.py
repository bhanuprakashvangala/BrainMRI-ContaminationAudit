"""Shared helpers: file listing, MD5, and the normalized cross-correlation (NCC) duplicate criterion.

Duplicate criterion (paper, Section III-A): each image is reduced to a 64x64 gray-scale array,
mean-centred and scaled to unit L2 norm; the inner product of two such vectors is their zero-mean
normalized cross-correlation rho in [-1, 1]. A test image is a near-duplicate when its best match in
the reference set has rho >= 0.98. The paper does not name the resampling filter; Lanczos
reproduces the published counts exactly, so it is used here.
"""
import hashlib
import os

import numpy as np
from PIL import Image

IMG_EXT = (".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff")
SIDE = 64


def list_images(root):
    """All image files under root, as sorted absolute paths."""
    out = []
    for dirpath, _, files in os.walk(root):
        if "__MACOSX" in dirpath:
            continue
        for f in files:
            if f.lower().endswith(IMG_EXT) and not f.startswith("._"):
                out.append(os.path.join(dirpath, f))
    return sorted(out)


def md5(path):
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def ncc_vectors(paths):
    """(n, 4096) float32 matrix of mean-centred, unit-norm 64x64 gray-scale images."""
    V = np.zeros((len(paths), SIDE * SIDE), np.float32)
    for i, p in enumerate(paths):
        with Image.open(p) as im:
            a = np.asarray(im.convert("L").resize((SIDE, SIDE), Image.LANCZOS), np.float32).ravel()
        a = a - a.mean()
        n = np.linalg.norm(a)
        V[i] = a / n if n > 0 else a
    return V


def best_match(Q, R, block=2048):
    """For each row of Q, the maximum NCC against any row of R and the index of that row."""
    best = np.full(len(Q), -np.inf, np.float32)
    arg = np.zeros(len(Q), np.int64)
    for s in range(0, len(Q), block):
        S = Q[s:s + block] @ R.T
        arg[s:s + block] = S.argmax(1)
        best[s:s + block] = S.max(1)
    return best, arg


def dhash_bits(paths):
    """64-bit difference hash (9x8 gray-scale, Lanczos), as an (n, 64) 0/1 array."""
    out = np.zeros((len(paths), 64), np.uint8)
    for i, p in enumerate(paths):
        with Image.open(p) as im:
            a = np.asarray(im.convert("L").resize((9, 8), Image.LANCZOS), np.int16)
        out[i] = (a[:, 1:] > a[:, :-1]).ravel()
    return out


def min_hamming(Q, R, block=256):
    """For each row of Q, the smallest Hamming distance to any row of R."""
    out = np.zeros(len(Q), np.int64)
    for s in range(0, len(Q), block):
        out[s:s + block] = (Q[s:s + block, None, :] != R[None, :, :]).sum(2).min(1)
    return out


def rel(path, root):
    return os.path.relpath(path, root).replace(os.sep, "/")
