# Phase 4 Evaluation Report

Generated at: 2026-06-07T09:03:09.283178+00:00

## Model

- Model name: IndoBERT base p1
- Model directory: models/indobert-medical-ner-id
- Test file: data\annotated\test.conll

## Overall Metrics

- Sentences: 1306
- Tokens: 10337
- Token accuracy: 0.9931
- Sentence exact match: 0.9609
- Micro precision: 0.9556
- Micro recall: 0.9765
- Micro F1: 0.9659

## Metrics per Entity

| Entity | Precision | Recall | F1 | Support |
| --- | ---: | ---: | ---: | ---: |
| ANATOMI | 0.9615 | 1.0000 | 0.9804 | 425 |
| DIAGNOSIS | 0.9836 | 0.9231 | 0.9524 | 65 |
| DOSIS | 0.8627 | 0.9778 | 0.9167 | 45 |
| GEJALA | 0.9527 | 0.9650 | 0.9588 | 543 |
| OBAT | 0.9853 | 0.9710 | 0.9781 | 69 |

## Artifacts

- Full metrics JSON: reports/evaluation_indobert_metrics.json
- Token-level confusion matrix: reports/evaluation_indobert_confusion_matrix.csv
- Correct and incorrect examples: reports/evaluation_indobert_prediction_examples.jsonl

## Caveat

These metrics evaluate the Phase 3 bootstrap model against the semi-automatic
Phase 2 labels. They are useful for engineering progress, but final claims still
need manually reviewed labels.
