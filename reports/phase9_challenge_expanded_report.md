# Phase 4 Evaluation Report

Generated at: 2026-06-16T14:07:20.386515+00:00

## Model

- Model name: IndoBERT base p1 phase9-expanded
- Model directory: models/indobert-medical-ner-id-phase9-expanded
- Test file: data\phase9_challenge_set\gold_resolved.conll

## Overall Metrics

- Sentences: 160
- Tokens: 1366
- Token accuracy: 0.7716
- Sentence exact match: 0.2000
- Micro precision: 0.7422
- Micro recall: 0.6338
- Micro F1: 0.6837

## Metrics per Entity

| Entity | Precision | Recall | F1 | Support |
| --- | ---: | ---: | ---: | ---: |
| ALERGI | 0.8649 | 0.9697 | 0.9143 | 33 |
| ANATOMI | 0.8305 | 0.8033 | 0.8167 | 61 |
| DIAGNOSIS | 0.7727 | 0.4722 | 0.5862 | 36 |
| DOSIS | 0.0000 | 0.0000 | 0.0000 | 3 |
| GEJALA | 0.8842 | 0.5833 | 0.7029 | 144 |
| HASIL_LAB | 0.8636 | 0.7308 | 0.7917 | 26 |
| NILAI_LAB | 0.8333 | 0.7143 | 0.7692 | 14 |
| OBAT | 0.7831 | 0.7065 | 0.7429 | 92 |
| PROSEDUR | 0.6429 | 0.4655 | 0.5400 | 58 |
| RIWAYAT_PENYAKIT | 0.0000 | 0.0000 | 0.0000 | 21 |
| WAKTU_DURASI | 0.4026 | 0.7949 | 0.5345 | 39 |

## Artifacts

- Full metrics JSON: reports/phase9_challenge_expanded_metrics.json
- Token-level confusion matrix: reports/phase9_challenge_expanded_confusion_matrix.csv
- Correct and incorrect examples: reports/phase9_challenge_expanded_prediction_examples.jsonl

## Caveat

These metrics evaluate the model against the Phase 9 internal challenge set. This set includes expanded labels that older 5-label models were not trained to predict, so treat the result as a stress test and schema-gap report, not as formal clinical validation.
