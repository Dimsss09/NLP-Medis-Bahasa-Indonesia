# Phase 4 Evaluation Report

Generated at: 2026-06-07T23:27:30.661084+00:00

## Model

- Model name: IndoBERT base p1
- Model directory: models/indobert-medical-ner-id
- Test file: data\annotated\test.conll

## Overall Metrics

- Sentences: 1306
- Tokens: 10337
- Token accuracy: 0.9998
- Sentence exact match: 0.9992
- Micro precision: 1.0000
- Micro recall: 0.9991
- Micro F1: 0.9996

## Metrics per Entity

| Entity | Precision | Recall | F1 | Support |
| --- | ---: | ---: | ---: | ---: |
| ANATOMI | 1.0000 | 1.0000 | 1.0000 | 425 |
| DIAGNOSIS | 1.0000 | 1.0000 | 1.0000 | 65 |
| DOSIS | 1.0000 | 0.9778 | 0.9888 | 45 |
| GEJALA | 1.0000 | 1.0000 | 1.0000 | 543 |
| OBAT | 1.0000 | 1.0000 | 1.0000 | 69 |

## Artifacts

- Full metrics JSON: reports/evaluation_indobert_metrics.json
- Token-level confusion matrix: reports/evaluation_indobert_confusion_matrix.csv
- Correct and incorrect examples: reports/evaluation_indobert_prediction_examples.jsonl

## Caveat

These metrics evaluate the Phase 3 bootstrap model against the semi-automatic
Phase 2 labels. They are useful for engineering progress, but final claims still
need manually reviewed labels.
