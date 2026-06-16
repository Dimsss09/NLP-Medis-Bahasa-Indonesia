# Phase 4 Evaluation Report

Generated at: 2026-06-16T14:02:55.221753+00:00

## Model

- Model name: IndoBERT base p1 human-aligned
- Model directory: models/indobert-medical-ner-id-human-aligned
- Test file: data\phase9_challenge_set\gold_resolved.conll

## Overall Metrics

- Sentences: 160
- Tokens: 1366
- Token accuracy: 0.6859
- Sentence exact match: 0.0563
- Micro precision: 0.6935
- Micro recall: 0.4080
- Micro F1: 0.5137

## Metrics per Entity

| Entity | Precision | Recall | F1 | Support |
| --- | ---: | ---: | ---: | ---: |
| ALERGI | 0.0000 | 0.0000 | 0.0000 | 33 |
| ANATOMI | 0.8305 | 0.8033 | 0.8167 | 61 |
| DIAGNOSIS | 0.2615 | 0.4722 | 0.3366 | 36 |
| DOSIS | 0.0000 | 0.0000 | 0.0000 | 3 |
| GEJALA | 0.8842 | 0.5833 | 0.7029 | 144 |
| HASIL_LAB | 0.0000 | 0.0000 | 0.0000 | 26 |
| NILAI_LAB | 0.0000 | 0.0000 | 0.0000 | 14 |
| OBAT | 0.7143 | 0.7065 | 0.7104 | 92 |
| PROSEDUR | 0.0000 | 0.0000 | 0.0000 | 58 |
| RIWAYAT_PENYAKIT | 0.0000 | 0.0000 | 0.0000 | 21 |
| WAKTU_DURASI | 0.0000 | 0.0000 | 0.0000 | 39 |

## Artifacts

- Full metrics JSON: reports/phase9_challenge_human_aligned_metrics.json
- Token-level confusion matrix: reports/phase9_challenge_human_aligned_confusion_matrix.csv
- Correct and incorrect examples: reports/phase9_challenge_human_aligned_prediction_examples.jsonl

## Caveat

These metrics evaluate the model against the Phase 9 internal challenge set. This set includes expanded labels that older 5-label models were not trained to predict, so treat the result as a stress test and schema-gap report, not as formal clinical validation.
