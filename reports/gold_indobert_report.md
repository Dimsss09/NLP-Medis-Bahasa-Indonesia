# Phase 4 Evaluation Report

Generated at: 2026-06-07T23:28:36.805675+00:00

## Model

- Model name: IndoBERT base p1
- Model directory: models/indobert-medical-ner-id
- Test file: data\manual_gold\gold_resolved.conll

## Overall Metrics

- Sentences: 400
- Tokens: 3194
- Token accuracy: 0.9994
- Sentence exact match: 0.9975
- Micro precision: 1.0000
- Micro recall: 0.9974
- Micro F1: 0.9987

## Metrics per Entity

| Entity | Precision | Recall | F1 | Support |
| --- | ---: | ---: | ---: | ---: |
| ANATOMI | 1.0000 | 1.0000 | 1.0000 | 140 |
| DIAGNOSIS | 1.0000 | 1.0000 | 1.0000 | 18 |
| DOSIS | 1.0000 | 0.9286 | 0.9630 | 14 |
| GEJALA | 1.0000 | 1.0000 | 1.0000 | 184 |
| OBAT | 1.0000 | 1.0000 | 1.0000 | 22 |

## Artifacts

- Full metrics JSON: reports/gold_indobert_metrics.json
- Token-level confusion matrix: reports/gold_indobert_confusion_matrix.csv
- Correct and incorrect examples: reports/gold_indobert_prediction_examples.jsonl

## Caveat

These metrics evaluate the Phase 3 bootstrap model against the semi-automatic
Phase 2 labels. They are useful for engineering progress, but final claims still
need manually reviewed labels.
