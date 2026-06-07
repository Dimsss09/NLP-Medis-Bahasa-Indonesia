# Phase 3 Training Summary

Generated at: 2026-06-07T23:26:42.518513+00:00

## Shared Setup

- Labels: O, B-GEJALA, I-GEJALA, B-OBAT, I-OBAT, B-DOSIS, I-DOSIS, B-DIAGNOSIS, I-DIAGNOSIS, B-ANATOMI, I-ANATOMI
- Data source: silver
- Hyperparameters are read once from `training` in `config.yaml` and reused for every model to keep the comparison fair.

## Model Runs

| Model key | Role | Base model | Output dir | Train loss | Validation loss | Validation token accuracy |
| --- | --- | --- | --- | ---: | ---: | ---: |
| indobert | utama | indobenchmark/indobert-base-p1 | models\indobert-medical-ner-id | 0.0010 | 0.0000 | 1.0000 |
| xlm_roberta | pembanding | xlm-roberta-base | models\xlm-roberta-medical-ner-id | 0.0311 | 0.0098 | 0.9978 |

## IndoBERT base p1 (`indobert`)

- Role: utama
- Base model: indobenchmark/indobert-base-p1
- Output directory: models\indobert-medical-ner-id
- Device: cuda
- Training data source: silver
- Training file: data/silver/train.conll
- Validation file: data/silver/val.conll
- Train sentences used: 10441
- Validation sentences used: 512
- Last train loss: 0.0010
- Last validation loss: 0.0000
- Last validation token accuracy: 1.0000

## XLM-RoBERTa base (`xlm_roberta`)

- Role: pembanding
- Base model: xlm-roberta-base
- Output directory: models\xlm-roberta-medical-ner-id
- Device: cuda
- Training data source: silver
- Training file: data/silver/train.conll
- Validation file: data/silver/val.conll
- Train sentences used: 10441
- Validation sentences used: 512
- Last train loss: 0.0311
- Last validation loss: 0.0098
- Last validation token accuracy: 0.9978


## Notes

This is a bootstrap training setup on silver labels. `xlm-roberta-base` has a
larger memory footprint than IndoBERT; if GPU memory is limited, lower
`training.per_device_train_batch_size` and rerun the same config for both
models.
