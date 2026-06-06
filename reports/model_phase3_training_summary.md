# Phase 3 Training Summary

Generated at: 2026-06-06T18:37:33.872146+00:00

## Model

- Base model: indobenchmark/indobert-base-p1
- Output directory: models\indobert-medical-ner-id
- Device: cpu

## Data

- Train sentences used: 2048
- Validation sentences used: 512
- Labels: O, B-GEJALA, I-GEJALA, B-OBAT, I-OBAT, B-DOSIS, I-DOSIS, B-DIAGNOSIS, I-DIAGNOSIS, B-ANATOMI, I-ANATOMI

## Last Epoch

- Train loss: 0.1795
- Validation loss: 0.0213
- Validation token accuracy: 0.9953

## Notes

This is a bootstrap training run on semi-automatic Phase 2 labels. Use Phase 4
evaluation and a manually resolved gold test set before making any performance
claims.
