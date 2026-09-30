# Data

No images are included in this repository. All corpora are public and are downloaded with

```bash
python data/download.py              # the four Kaggle corpora, via kagglehub
python data/download.py --figshare   # also the figshare release, for the patient audit
```

The Kaggle images stay in the kagglehub cache; `data/paths.json` records where they are. The figshare
files go to `data/figshare/`. Both are ignored by git.

| Role in the paper | Dataset | Source | Version |
|---|---|---|---|
| C1 (Nickparvar), 5,600 train / 1,600 test, 4 classes | Brain Tumor MRI Dataset | [kaggle.com/datasets/masoudnickparvar/brain-tumor-mri-dataset](https://www.kaggle.com/datasets/masoudnickparvar/brain-tumor-mri-dataset) | 2 |
| C2 (SARTAJ), 2,870 train / 394 test, 4 classes | Brain Tumor Classification (MRI) | [kaggle.com/datasets/sartajbhuvaji/brain-tumor-classification-mri](https://www.kaggle.com/datasets/sartajbhuvaji/brain-tumor-classification-mri) | 3 |
| C3 (Navoneel), 253 images, yes/no | Brain MRI Images for Brain Tumor Detection | [kaggle.com/datasets/navoneel/brain-mri-images-for-brain-tumor-detection](https://www.kaggle.com/datasets/navoneel/brain-mri-images-for-brain-tumor-detection) | 1 |
| Negative control, 5,216 train / 624 test | Chest X-Ray Images (Pneumonia), Kermany et al. 2018 | [kaggle.com/datasets/paultimothymooney/chest-xray-pneumonia](https://www.kaggle.com/datasets/paultimothymooney/chest-xray-pneumonia) | 2 |
| Patient keys (cjdata.PID), 3,064 slices | Brain tumor dataset, Cheng et al. | [doi.org/10.6084/m9.figshare.1512427](https://doi.org/10.6084/m9.figshare.1512427) (CC BY 4.0) | 8 |

Public Kaggle datasets can usually be downloaded without an account. If kagglehub asks for credentials, set the
`KAGGLE_USERNAME` and `KAGGLE_KEY` environment variables; never commit them.

Please follow each dataset's license and cite the original authors.
