# Notebooks

Exploratory analysis lives in reproducible scripts rather than notebooks, so
every number in the README can be regenerated from CI:

- `ml/scripts/download_dataset.py` — dataset acquisition + manifest
- `ml/scripts/prepare_dataset.py` — stratified split + distribution report
- `ml/training/train.py` — training, evaluation, ablation and charts

Add notebooks here for one-off experiments only; keep anything load-bearing
in the scripts above.
