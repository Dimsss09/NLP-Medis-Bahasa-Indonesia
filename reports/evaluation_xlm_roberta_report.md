# Phase 4 Evaluation Report

Generated at: 2026-06-07T23:27:39.815520+00:00

## Model

- Model name: XLM-RoBERTa base
- Model directory: models/xlm-roberta-medical-ner-id
- Test file: data\annotated\test.conll

## Overall Metrics

- Sentences: 1306
- Tokens: 10337
- Token accuracy: 0.9965
- Sentence exact match: 0.9763
- Micro precision: 0.9656
- Micro recall: 0.9782
- Micro F1: 0.9718

## Metrics per Entity

| Entity | Precision | Recall | F1 | Support |
| --- | ---: | ---: | ---: | ---: |
| ANATOMI | 0.9654 | 0.9835 | 0.9744 | 425 |
| DIAGNOSIS | 0.9848 | 1.0000 | 0.9924 | 65 |
| DOSIS | 0.9167 | 0.9778 | 0.9462 | 45 |
| GEJALA | 0.9670 | 0.9705 | 0.9688 | 543 |
| OBAT | 0.9714 | 0.9855 | 0.9784 | 69 |

## Artifacts

- Full metrics JSON: reports/evaluation_xlm_roberta_metrics.json
- Token-level confusion matrix: reports/evaluation_xlm_roberta_confusion_matrix.csv
- Correct and incorrect examples: reports/evaluation_xlm_roberta_prediction_examples.jsonl

## Caveat

These metrics evaluate the Phase 3 bootstrap model against the semi-automatic
Phase 2 labels. They are useful for engineering progress, but final claims still
need manually reviewed labels.
