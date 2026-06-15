# Phase 4 Model Comparison

Generated at: 2026-06-15T08:36:15.617981+00:00

## Overall Metrics

| Model key | Role | Base model | Model dir | Micro precision | Micro recall | Micro F1 |
| --- | --- | --- | --- | ---: | ---: | ---: |
| indobert | utama | indobenchmark/indobert-base-p1 | models/indobert-medical-ner-id | 0.6538 | 0.2530 | 0.3649 |
| xlm_roberta | pembanding | xlm-roberta-base | models/xlm-roberta-medical-ner-id | 0.6367 | 0.2395 | 0.3481 |

## F1 per Entity

| Entity | indobert F1 | xlm_roberta F1 |
| --- | ---: | ---: |
| ANATOMI | 0.5391 | 0.5197 |
| DIAGNOSIS | 0.1905 | 0.1905 |
| DOSIS | 0.0000 | 0.0000 |
| GEJALA | 0.4184 | 0.3941 |
| OBAT | 0.0970 | 0.0970 |

## Compact F1 Chart

- ANATOMI / indobert: `###########---------` 0.5391
- ANATOMI / xlm_roberta: `##########----------` 0.5197
- DIAGNOSIS / indobert: `####----------------` 0.1905
- DIAGNOSIS / xlm_roberta: `####----------------` 0.1905
- DOSIS / indobert: `--------------------` 0.0000
- DOSIS / xlm_roberta: `--------------------` 0.0000
- GEJALA / indobert: `########------------` 0.4184
- GEJALA / xlm_roberta: `########------------` 0.3941
- OBAT / indobert: `##------------------` 0.0970
- OBAT / xlm_roberta: `##------------------` 0.0970

## Trade-off Notes

- `indobert` is the primary Indonesian model and is expected to be lighter for this Bahasa Indonesia-only task.
- `xlm_roberta` is the multilingual comparator. It is larger and can need a smaller batch size on limited GPU memory.
- Use the same data split and hyperparameters for both runs before making the comparison table final.

## Artifacts

- CSV comparison table: `reports/model_comparison.csv`
- Per-model JSON, confusion matrix, examples, and Markdown reports are stored with `reports/evaluation_<model_key>_*` names.
