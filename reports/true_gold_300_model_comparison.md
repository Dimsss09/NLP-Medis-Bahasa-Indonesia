# True Gold 300 Model Comparison

Generated at: 2026-06-15

All models below are evaluated on the same manually adjudicated benchmark:

```text
data/true_gold_300/gold_resolved.conll
```

## Overall Metrics

| Model | Training source | Precision | Recall | Micro F1 | Token accuracy | Sentence exact match |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| IndoBERT human-aligned | `data/human_aligned_silver/` | 0.7967 | 0.6631 | 0.7238 | 0.8419 | 0.3800 |
| IndoBERT baseline | `data/silver/` | 0.6538 | 0.2530 | 0.3649 | 0.6558 | 0.0733 |
| XLM-RoBERTa baseline | `data/silver/` | 0.6367 | 0.2395 | 0.3481 | 0.6509 | 0.0567 |

## Per-Entity F1

| Entity | IndoBERT human-aligned | IndoBERT baseline | XLM-RoBERTa baseline |
| --- | ---: | ---: | ---: |
| ANATOMI | 0.8333 | 0.5391 | 0.5197 |
| DIAGNOSIS | 0.8364 | 0.1905 | 0.1905 |
| DOSIS | 0.4706 | 0.0000 | 0.0000 |
| GEJALA | 0.6897 | 0.4184 | 0.3941 |
| OBAT | 0.6214 | 0.0970 | 0.0970 |

## Interpretation

The human-aligned retraining is the first model version that meaningfully
generalizes toward the adjudicated human labels. It improves micro F1 by 0.3589
absolute points over the IndoBERT baseline.

Remaining priorities:

- Add more manually reviewed `DOSIS` examples.
- Improve `GEJALA` recall.
- Review whether product/cosmetic mentions should remain under `OBAT` for the
  final thesis/portfolio scope.
