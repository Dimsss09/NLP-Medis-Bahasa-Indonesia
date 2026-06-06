# Phase 4 Evaluation Report

Generated at: 2026-06-06T18:09:05.035248+00:00

## Model

- Model directory: models/indobert-medical-ner-id
- Test file: data/annotated/test.conll

## Overall Metrics

- Sentences: 1306
- Tokens: 10337
- Token accuracy: 0.9510
- Sentence exact match: 0.7351
- Micro precision: 0.7917
- Micro recall: 0.7524
- Micro F1: 0.7716

## Metrics per Entity

| Entity | Precision | Recall | F1 | Support |
| --- | ---: | ---: | ---: | ---: |
| ANATOMI | 0.8184 | 0.8800 | 0.8481 | 425 |
| DIAGNOSIS | 1.0000 | 0.2769 | 0.4337 | 65 |
| DOSIS | 0.0000 | 0.0000 | 0.0000 | 45 |
| GEJALA | 0.7640 | 0.8527 | 0.8059 | 543 |
| OBAT | 1.0000 | 0.1159 | 0.2078 | 69 |

## Artifacts

- Full metrics JSON: reports/evaluation_metrics.json
- Token-level confusion matrix: reports/confusion_matrix.csv
- Correct and incorrect examples: reports/prediction_examples.jsonl

## Caveat

These metrics evaluate the Phase 3 bootstrap model against the semi-automatic
Phase 2 labels. They are useful for engineering progress, but final claims still
need manually reviewed labels.
