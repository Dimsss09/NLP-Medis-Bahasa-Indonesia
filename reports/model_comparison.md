# Phase 4 Model Comparison

Generated at: 2026-06-07T23:28:40.606918+00:00

## Overall Metrics

| Model key | Role | Base model | Model dir | Micro precision | Micro recall | Micro F1 |
| --- | --- | --- | --- | ---: | ---: | ---: |
| indobert | utama | indobenchmark/indobert-base-p1 | models/indobert-medical-ner-id | 1.0000 | 0.9974 | 0.9987 |
| xlm_roberta | pembanding | xlm-roberta-base | models/xlm-roberta-medical-ner-id | 0.9762 | 0.9762 | 0.9762 |

## F1 per Entity

| Entity | indobert F1 | xlm_roberta F1 |
| --- | ---: | ---: |
| ANATOMI | 1.0000 | 0.9714 |
| DIAGNOSIS | 1.0000 | 1.0000 |
| DOSIS | 0.9630 | 0.9630 |
| GEJALA | 1.0000 | 0.9756 |
| OBAT | 1.0000 | 1.0000 |

## Compact F1 Chart

- ANATOMI / indobert: `####################` 1.0000
- ANATOMI / xlm_roberta: `###################-` 0.9714
- DIAGNOSIS / indobert: `####################` 1.0000
- DIAGNOSIS / xlm_roberta: `####################` 1.0000
- DOSIS / indobert: `###################-` 0.9630
- DOSIS / xlm_roberta: `###################-` 0.9630
- GEJALA / indobert: `####################` 1.0000
- GEJALA / xlm_roberta: `####################` 0.9756
- OBAT / indobert: `####################` 1.0000
- OBAT / xlm_roberta: `####################` 1.0000

## Trade-off Notes

- `indobert` is the primary Indonesian model and is expected to be lighter for this Bahasa Indonesia-only task.
- `xlm_roberta` is the multilingual comparator. It is larger and can need a smaller batch size on limited GPU memory.
- Use the same data split and hyperparameters for both runs before making the comparison table final.

## Artifacts

- CSV comparison table: `reports/model_comparison.csv`
- Per-model JSON, confusion matrix, examples, and Markdown reports are stored with `reports/evaluation_<model_key>_*` names.
