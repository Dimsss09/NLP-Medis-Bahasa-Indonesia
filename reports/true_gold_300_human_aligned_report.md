# Phase 4 Evaluation Report

Generated at: 2026-06-15T08:51:29.184881+00:00

## Model

- Model name: IndoBERT base p1 human-aligned
- Model directory: models/indobert-medical-ner-id-human-aligned
- Test file: data\true_gold_300\gold_resolved.conll

## Overall Metrics

- Sentences: 300
- Tokens: 2403
- Token accuracy: 0.8419
- Sentence exact match: 0.3800
- Micro precision: 0.7967
- Micro recall: 0.6631
- Micro F1: 0.7238

## Metrics per Entity

| Entity | Precision | Recall | F1 | Support |
| --- | ---: | ---: | ---: | ---: |
| ANATOMI | 0.8228 | 0.8442 | 0.8333 | 154 |
| DIAGNOSIS | 0.9452 | 0.7500 | 0.8364 | 92 |
| DOSIS | 0.5714 | 0.4000 | 0.4706 | 10 |
| GEJALA | 0.8130 | 0.5988 | 0.6897 | 334 |
| OBAT | 0.6641 | 0.5839 | 0.6214 | 149 |

## Artifacts

- Full metrics JSON: reports/true_gold_300_human_aligned_metrics.json
- Token-level confusion matrix: reports/true_gold_300_human_aligned_confusion_matrix.csv
- Correct and incorrect examples: reports/true_gold_300_human_aligned_prediction_examples.jsonl

## Caveat

These metrics evaluate the model against a manually adjudicated human gold set. They are suitable for prototype research reporting, but they are not a formal clinical validation.
