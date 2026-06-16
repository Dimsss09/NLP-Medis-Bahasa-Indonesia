# Phase 4 Evaluation Report

Generated at: 2026-06-16T14:07:57.710710+00:00

## Model

- Model name: IndoBERT base p1 phase9-expanded
- Model directory: models/indobert-medical-ner-id-phase9-expanded
- Test file: data\true_gold_300\gold_resolved.conll

## Overall Metrics

- Sentences: 300
- Tokens: 2403
- Token accuracy: 0.7790
- Sentence exact match: 0.1967
- Micro precision: 0.6304
- Micro recall: 0.6346
- Micro F1: 0.6325

## Metrics per Entity

| Entity | Precision | Recall | F1 | Support |
| --- | ---: | ---: | ---: | ---: |
| ALERGI | 0.0000 | 0.0000 | 0.0000 | 0 |
| ANATOMI | 0.8302 | 0.8571 | 0.8435 | 154 |
| DIAGNOSIS | 0.8929 | 0.5435 | 0.6757 | 92 |
| DOSIS | 0.5714 | 0.4000 | 0.4706 | 10 |
| GEJALA | 0.8056 | 0.6078 | 0.6928 | 334 |
| HASIL_LAB | 0.0000 | 0.0000 | 0.0000 | 0 |
| NILAI_LAB | 0.0000 | 0.0000 | 0.0000 | 0 |
| OBAT | 0.6299 | 0.5369 | 0.5797 | 149 |
| PROSEDUR | 0.0000 | 0.0000 | 0.0000 | 0 |
| WAKTU_DURASI | 0.0000 | 0.0000 | 0.0000 | 0 |

## Artifacts

- Full metrics JSON: reports/true_gold_300_phase9_expanded_metrics.json
- Token-level confusion matrix: reports/true_gold_300_phase9_expanded_confusion_matrix.csv
- Correct and incorrect examples: reports/true_gold_300_phase9_expanded_prediction_examples.jsonl

## Caveat

These metrics evaluate the model against a manually adjudicated human gold set. They are suitable for prototype research reporting, but they are not a formal clinical validation.
