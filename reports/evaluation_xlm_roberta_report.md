# Phase 4 Evaluation Report

Generated at: 2026-06-07T09:03:39.439262+00:00

## Model

- Model name: XLM-RoBERTa base
- Model directory: models/xlm-roberta-medical-ner-id
- Test file: data\annotated\test.conll

## Overall Metrics

- Sentences: 1306
- Tokens: 10337
- Token accuracy: 0.9465
- Sentence exact match: 0.7075
- Micro precision: 0.7144
- Micro recall: 0.7001
- Micro F1: 0.7072

## Metrics per Entity

| Entity | Precision | Recall | F1 | Support |
| --- | ---: | ---: | ---: | ---: |
| ANATOMI | 0.8096 | 0.9506 | 0.8745 | 425 |
| DIAGNOSIS | 0.0000 | 0.0000 | 0.0000 | 65 |
| DOSIS | 0.0000 | 0.0000 | 0.0000 | 45 |
| GEJALA | 0.6384 | 0.7348 | 0.6832 | 543 |
| OBAT | 0.0000 | 0.0000 | 0.0000 | 69 |

## Artifacts

- Full metrics JSON: reports/evaluation_xlm_roberta_metrics.json
- Token-level confusion matrix: reports/evaluation_xlm_roberta_confusion_matrix.csv
- Correct and incorrect examples: reports/evaluation_xlm_roberta_prediction_examples.jsonl

## Caveat

These metrics evaluate the Phase 3 bootstrap model against the semi-automatic
Phase 2 labels. They are useful for engineering progress, but final claims still
need manually reviewed labels.
