# Scores That Hold, Benchmarks That Leak

Audit code and results for **Scores That Hold, Benchmarks That Leak: Measuring Dataset Contamination in Public Brain-Tumor MRI Classification**
Bhanu Prakash Vangala, Sowmya Guda, Latha Peddi, Navya Vangala.
Under review at IEEE Journal of Biomedical and Health Informatics (JBHI).

The three most used Kaggle brain-tumor MRI corpora (Nickparvar, SARTAJ, Navoneel) reuse the same scans across their
training and test splits and across each other, and many test slices come from patients who are also in training.
This repository measures both, with the Kermany chest X-ray corpus as a negative control, and releases the
contaminated-file lists, the recovered patient keys and the deduplicated splits. Nothing here needs a GPU or a
trained model.

## Layout

```
data/        download script for the public corpora (no images are included)
src/         audit_duplicates.py   duplicate audit within and across corpora, file lists (Tables I-II)
             patient_leakage.py    patient-ID recovery from the figshare release (Tables III-IV)
             make_figures.py       plots of the audit results
             compare_to_paper.py   checks each audit number against the paper
             corpora.py, imaging.py  dataset paths, image loading, NCC and hashing helpers
scripts/     reproduce.py, the single entry point
results/     audit/            audit tables (CSV) and file lists (audit/lists/)
             figures/          plots made by make_figures.py
```

## Setup

```bash
git clone https://github.com/bhanuprakashvangala/BrainMRI-ContaminationAudit.git
cd BrainMRI-ContaminationAudit
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Reproduce

```bash
python scripts/reproduce.py --patients
```

This downloads the four Kaggle corpora (about 2.6 GB, into the kagglehub cache) and the figshare release (about
880 MB, into `data/figshare/`), runs both audits, draws the figures and checks every number against the paper. It
takes about 15 minutes on a laptop CPU plus download time. Without `--patients` the figshare download and the patient
audit are skipped. See `data/README.md` for the dataset sources.

## Results

All values below are recomputed by `scripts/reproduce.py` and equal the values in the paper
(`python src/compare_to_paper.py` checks all 27).

Duplicates (a test image counts as leaked when a training image has normalized cross-correlation >= 0.98):

| | |
|---|---|
| Nickparvar test images with a near-twin in training | 460 of 1,600 (28.75%) |
| Nickparvar test images still flagged at NCC >= 0.995 | 432 |
| SARTAJ test images byte-identical to a training image | 88 of 394 (22.34%) |
| SARTAJ test images with a near-twin in training | 65.74% |
| Kermany chest X-ray control, exact / near-twins | 0 / 0 |
| SARTAJ images contained in Nickparvar, exact / near | 2,670 (81.8%) / 2,705 (82.87%) |
| Navoneel images contained in Nickparvar, exact / near | 66 / 123 (48.62%) |
| Navoneel images contained in SARTAJ, near | 98 (38.74%) |
| Deduplicated Nickparvar test split / cleaned SARTAJ / cleaned Navoneel | 1,140 / 559 / 130 images |

Patients (recovered from `cjdata.PID` in the figshare release, 3,064 slices from 233 patients):

| | |
|---|---|
| Nickparvar test images traceable to a figshare patient | 201 (12.56%), from 125 patients |
| of those, same patient also in training | 192 (95.52%) |
| SARTAJ test images traceable / same patient in training | 28 / 28 (100%) |

## Notes

- Images are resized to 64x64 with Lanczos resampling before the NCC comparison.
- A 64-bit difference hash at Hamming radius 5 flags 62.75% of the Nickparvar test split but also 93.27% of the
  chest X-ray control, which is why the audit uses NCC.
- `results/audit/lists/` holds the contaminated-file lists, the deduplicated Nickparvar test split, the cleaned
  SARTAJ and Navoneel sets and the recovered patient keys, as relative paths into the Kaggle datasets.
- The counts are for the Kaggle dataset versions pinned in `data/download.py`.

## Citation

```bibtex
@misc{vangala2026scores,
  title  = {Scores That Hold, Benchmarks That Leak: Measuring Dataset Contamination in Public Brain-Tumor MRI Classification},
  author = {Vangala, Bhanu Prakash and Guda, Sowmya and Peddi, Latha and Vangala, Navya},
  year   = {2026},
  note   = {Under review at IEEE Journal of Biomedical and Health Informatics}
}
```

## License

Code, tables and file lists: MIT. The image datasets are third-party and keep their own licenses; the patient keys
come from the figshare release of Cheng et al. (CC BY 4.0). See `data/README.md`.
