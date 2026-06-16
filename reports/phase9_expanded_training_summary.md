# Phase 3 Training Summary

Generated at: 2026-06-16T14:06:55.582397+00:00

## Shared Setup

- Labels: O, B-GEJALA, I-GEJALA, B-OBAT, I-OBAT, B-DOSIS, I-DOSIS, B-DIAGNOSIS, I-DIAGNOSIS, B-ANATOMI, I-ANATOMI, B-PROSEDUR, I-PROSEDUR, B-HASIL_LAB, I-HASIL_LAB, B-NILAI_LAB, I-NILAI_LAB, B-WAKTU_DURASI, I-WAKTU_DURASI, B-ALERGI, I-ALERGI, B-RIWAYAT_PENYAKIT, I-RIWAYAT_PENYAKIT
- Data source: silver
- Hyperparameters are read once from `training` in `config.yaml` and reused for every model to keep the comparison fair.

## Model Runs

| Model key | Role | Base model | Output dir | Train loss | Validation loss | Validation token accuracy |
| --- | --- | --- | --- | ---: | ---: | ---: |
| indobert | expanded-label | indobenchmark/indobert-base-p1 | models\indobert-medical-ner-id-phase9-expanded | 0.0066 | 0.0338 | 0.9953 |

## IndoBERT base p1 phase9-expanded (`indobert`)

- Role: expanded-label
- Base model: indobenchmark/indobert-base-p1
- Output directory: models\indobert-medical-ner-id-phase9-expanded
- Device: cuda
- Training data source: silver
- Training file: data/phase9_expanded_silver/train.conll
- Validation file: data/phase9_expanded_silver/val.conll
- Train sentences used: 11332
- Validation sentences used: 512
- Last train loss: 0.0066
- Last validation loss: 0.0338
- Last validation token accuracy: 0.9953


## Notes

This is a bootstrap training setup on silver labels. `xlm-roberta-base` has a
larger memory footprint than IndoBERT; if GPU memory is limited, lower
`training.per_device_train_batch_size` and rerun the same config for both
models.
