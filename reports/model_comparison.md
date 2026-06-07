# Phase 4 Model Comparison

Generated at: 2026-06-07T09:03:39.736541+00:00

## Overall Metrics

| Model key | Role | Base model | Model dir | Micro precision | Micro recall | Micro F1 |
| --- | --- | --- | --- | ---: | ---: | ---: |
| indobert | utama | indobenchmark/indobert-base-p1 | models/indobert-medical-ner-id | 0.9556 | 0.9765 | 0.9659 |
| xlm_roberta | pembanding | xlm-roberta-base | models/xlm-roberta-medical-ner-id | 0.7144 | 0.7001 | 0.7072 |

## F1 per Entity

| Entity | indobert F1 | xlm_roberta F1 |
| --- | ---: | ---: |
| ANATOMI | 0.9804 | 0.8745 |
| DIAGNOSIS | 0.9524 | 0.0000 |
| DOSIS | 0.9167 | 0.0000 |
| GEJALA | 0.9588 | 0.6832 |
| OBAT | 0.9781 | 0.0000 |

## Compact F1 Chart

- ANATOMI / indobert: `####################` 0.9804
- ANATOMI / xlm_roberta: `#################---` 0.8745
- DIAGNOSIS / indobert: `###################-` 0.9524
- DIAGNOSIS / xlm_roberta: `--------------------` 0.0000
- DOSIS / indobert: `##################--` 0.9167
- DOSIS / xlm_roberta: `--------------------` 0.0000
- GEJALA / indobert: `###################-` 0.9588
- GEJALA / xlm_roberta: `##############------` 0.6832
- OBAT / indobert: `####################` 0.9781
- OBAT / xlm_roberta: `--------------------` 0.0000

## Trade-off Notes

- `indobert` is the primary Indonesian model and is expected to be lighter for this Bahasa Indonesia-only task.
- `xlm_roberta` is the multilingual comparator. It is larger and can need a smaller batch size on limited GPU memory.
- Use the same data split and hyperparameters for both runs before making the comparison table final.

## Artifacts

- CSV comparison table: `reports/model_comparison.csv`
- Per-model JSON, confusion matrix, examples, and Markdown reports are stored with `reports/evaluation_<model_key>_*` names.
