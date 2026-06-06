# Phase 3 Training Summary

Generated at: 2026-06-06T17:53:01.864685+00:00

## Model

- Base model: indobenchmark/indobert-base-p1
- Output directory: models\indobert-medical-ner-id
- Device: cpu

## Data

- Train sentences used: 512
- Validation sentences used: 128
- Labels: O, B-GEJALA, I-GEJALA, B-OBAT, I-OBAT, B-DOSIS, I-DOSIS, B-DIAGNOSIS, I-DIAGNOSIS, B-ANATOMI, I-ANATOMI

## Last Epoch

- Train loss: 0.4110
- Validation loss: 0.1651
- Validation token accuracy: 0.9468

## Notes

This is the first bootstrap training run on semi-automatic Phase 2 labels. Use
Phase 4 evaluation before making any performance claims.
