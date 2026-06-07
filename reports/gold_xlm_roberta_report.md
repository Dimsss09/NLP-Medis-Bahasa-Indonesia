# Phase 4 Evaluation Report

Generated at: 2026-06-07T23:28:40.419722+00:00

## Model

- Model name: XLM-RoBERTa base
- Model directory: models/xlm-roberta-medical-ner-id
- Test file: data\manual_gold\gold_resolved.conll

## Overall Metrics

- Sentences: 400
- Tokens: 3194
- Token accuracy: 0.9969
- Sentence exact match: 0.9775
- Micro precision: 0.9762
- Micro recall: 0.9762
- Micro F1: 0.9762

## Metrics per Entity

| Entity | Precision | Recall | F1 | Support |
| --- | ---: | ---: | ---: | ---: |
| ANATOMI | 0.9714 | 0.9714 | 0.9714 | 140 |
| DIAGNOSIS | 1.0000 | 1.0000 | 1.0000 | 18 |
| DOSIS | 1.0000 | 0.9286 | 0.9630 | 14 |
| GEJALA | 0.9730 | 0.9783 | 0.9756 | 184 |
| OBAT | 1.0000 | 1.0000 | 1.0000 | 22 |

## Artifacts

- Full metrics JSON: reports/gold_xlm_roberta_metrics.json
- Token-level confusion matrix: reports/gold_xlm_roberta_confusion_matrix.csv
- Correct and incorrect examples: reports/gold_xlm_roberta_prediction_examples.jsonl

## Caveat

These metrics evaluate the Phase 3 bootstrap model against the semi-automatic
Phase 2 labels. They are useful for engineering progress, but final claims still
need manually reviewed labels.
