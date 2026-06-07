# Phase 3 Training Summary

Generated at: 2026-06-07T09:04:00+00:00

## Shared Setup

- Task: Indonesian medical NER token classification
- Training data source: silver
- Training file: data/silver/train.conll
- Validation file: data/silver/val.conll
- Train sentences used per model: 2048
- Validation sentences used per model: 512
- Epochs: 1
- Train batch size: 4
- Eval batch size: 4
- Max length: 128
- Learning rate: 0.00002
- Seed: 42

The same split and training hyperparameters were used for both models so Phase 4
can compare them fairly.

## Model Runs

| Model key | Role | Base model | Output dir | Device | Train loss | Validation loss | Validation token accuracy |
| --- | --- | --- | --- | --- | ---: | ---: | ---: |
| indobert | utama | indobenchmark/indobert-base-p1 | models/indobert-medical-ner-id | cpu | 0.1795 | 0.0213 | 0.9953 |
| xlm_roberta | pembanding | xlm-roberta-base | models/xlm-roberta-medical-ner-id | cpu | 0.3969 | 0.1597 | 0.9532 |

## Notes

`xlm-roberta-base` is larger than IndoBERT and took longer to train on CPU. If
GPU memory is limited in future runs, lower `training.per_device_train_batch_size`
and rerun both model keys with the same value before updating comparison claims.
