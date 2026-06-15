# Phase 3 Training Summary

Generated at: 2026-06-15T08:51:00.251321+00:00

## Shared Setup

- Labels: O, B-GEJALA, I-GEJALA, B-OBAT, I-OBAT, B-DOSIS, I-DOSIS, B-DIAGNOSIS, I-DIAGNOSIS, B-ANATOMI, I-ANATOMI
- Data source: annotated
- Hyperparameters are read once from `training` in `config.yaml` and reused for every model to keep the comparison fair.

## Model Runs

| Model key | Role | Base model | Output dir | Train loss | Validation loss | Validation token accuracy |
| --- | --- | --- | --- | ---: | ---: | ---: |
| indobert | utama | indobenchmark/indobert-base-p1 | models\indobert-medical-ner-id-human-aligned | 0.0039 | 0.0182 | 0.9970 |

## IndoBERT base p1 human-aligned (`indobert`)

- Role: utama
- Base model: indobenchmark/indobert-base-p1
- Output directory: models\indobert-medical-ner-id-human-aligned
- Device: cuda
- Training data source: annotated
- Training file: data/human_aligned_silver/train.conll
- Validation file: data/human_aligned_silver/val.conll
- Train sentences used: 11476
- Validation sentences used: 512
- Last train loss: 0.0039
- Last validation loss: 0.0182
- Last validation token accuracy: 0.9970


## Notes

This is a bootstrap training setup on silver labels. `xlm-roberta-base` has a
larger memory footprint than IndoBERT; if GPU memory is limited, lower
`training.per_device_train_batch_size` and rerun the same config for both
models.
