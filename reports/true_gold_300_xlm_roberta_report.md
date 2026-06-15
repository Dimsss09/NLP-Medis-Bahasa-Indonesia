# Phase 4 Evaluation Report

Generated at: 2026-06-15T08:36:15.405810+00:00

## Model

- Model name: XLM-RoBERTa base
- Model directory: models/xlm-roberta-medical-ner-id
- Test file: data\true_gold_300\gold_resolved.conll

## Overall Metrics

- Sentences: 300
- Tokens: 2403
- Token accuracy: 0.6509
- Sentence exact match: 0.0567
- Micro precision: 0.6367
- Micro recall: 0.2395
- Micro F1: 0.3481

## Metrics per Entity

| Entity | Precision | Recall | F1 | Support |
| --- | ---: | ---: | ---: | ---: |
| ANATOMI | 0.6600 | 0.4286 | 0.5197 | 154 |
| DIAGNOSIS | 0.7692 | 0.1087 | 0.1905 | 92 |
| DOSIS | 0.0000 | 0.0000 | 0.0000 | 10 |
| GEJALA | 0.6739 | 0.2784 | 0.3941 | 334 |
| OBAT | 0.5000 | 0.0537 | 0.0970 | 149 |

## Artifacts

- Full metrics JSON: reports/true_gold_300_xlm_roberta_metrics.json
- Token-level confusion matrix: reports/true_gold_300_xlm_roberta_confusion_matrix.csv
- Correct and incorrect examples: reports/true_gold_300_xlm_roberta_prediction_examples.jsonl

## Caveat

These metrics evaluate the model against a manually adjudicated human gold set. They are suitable for prototype research reporting, but they are not a formal clinical validation.
