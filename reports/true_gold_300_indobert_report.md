# Phase 4 Evaluation Report

Generated at: 2026-06-15T08:36:11.611518+00:00

## Model

- Model name: IndoBERT base p1
- Model directory: models/indobert-medical-ner-id
- Test file: data\true_gold_300\gold_resolved.conll

## Overall Metrics

- Sentences: 300
- Tokens: 2403
- Token accuracy: 0.6558
- Sentence exact match: 0.0733
- Micro precision: 0.6538
- Micro recall: 0.2530
- Micro F1: 0.3649

## Metrics per Entity

| Entity | Precision | Recall | F1 | Support |
| --- | ---: | ---: | ---: | ---: |
| ANATOMI | 0.6765 | 0.4481 | 0.5391 | 154 |
| DIAGNOSIS | 0.7692 | 0.1087 | 0.1905 | 92 |
| DOSIS | 0.0000 | 0.0000 | 0.0000 | 10 |
| GEJALA | 0.6944 | 0.2994 | 0.4184 | 334 |
| OBAT | 0.5000 | 0.0537 | 0.0970 | 149 |

## Artifacts

- Full metrics JSON: reports/true_gold_300_indobert_metrics.json
- Token-level confusion matrix: reports/true_gold_300_indobert_confusion_matrix.csv
- Correct and incorrect examples: reports/true_gold_300_indobert_prediction_examples.jsonl

## Caveat

These metrics evaluate the model against a manually adjudicated human gold set. They are suitable for prototype research reporting, but they are not a formal clinical validation.
