# True Gold 300 Evaluation Summary

Generated at: 2026-06-15

## Dataset Status

The project now has a manually adjudicated human gold set in
`data/true_gold_300/gold_resolved.conll`.

Gold set preparation:

- Source texts: 300 Indonesian medical-health questions.
- Annotators: 2 independent human annotators.
- Conflict resolution: manual adjudication in `conflicts_resolved.tsv`.
- Token count: 2403.
- Agreement before adjudication:
  - Token agreement: 0.8906.
  - Cohen's Kappa: 0.8290.
  - Entity F1 between annotators: 0.7532.
- Conflict count: 263.

This is suitable for prototype research reporting, but it is not a formal
clinical validation.

## True Gold Metrics

| Model | Precision | Recall | Micro F1 | Token accuracy | Sentence exact match |
| --- | ---: | ---: | ---: | ---: | ---: |
| IndoBERT human-aligned | 0.7967 | 0.6631 | 0.7238 | 0.8419 | 0.3800 |
| IndoBERT | 0.6538 | 0.2530 | 0.3649 | 0.6558 | 0.0733 |
| XLM-RoBERTa | 0.6367 | 0.2395 | 0.3481 | 0.6509 | 0.0567 |

## Human-Aligned IndoBERT Per-Entity Metrics

| Entity | Precision | Recall | F1 | Support |
| --- | ---: | ---: | ---: | ---: |
| ANATOMI | 0.8228 | 0.8442 | 0.8333 | 154 |
| DIAGNOSIS | 0.9452 | 0.7500 | 0.8364 | 92 |
| DOSIS | 0.5714 | 0.4000 | 0.4706 | 10 |
| GEJALA | 0.8130 | 0.5988 | 0.6897 | 334 |
| OBAT | 0.6641 | 0.5839 | 0.6214 | 149 |

## Interpretation

The baseline true-gold result was much lower than the previous silver-label
score. This confirmed that the original model overfit to automatic rules and
lexicons.

After building `data/human_aligned_silver/` from non-gold texts and retraining
IndoBERT, true-gold micro F1 improved from 0.3649 to 0.7238. The largest gains
were on `DIAGNOSIS`, `OBAT`, and `ANATOMI`.

Remaining gaps:

- `DOSIS` remains weak because it has only 10 gold examples.
- `GEJALA` recall is still below 0.60.
- The new training set is still automatic silver data, so future improvements
  should add more manually reviewed training examples.

## Recommended Next Phase

1. Keep `data/true_gold_300/gold_resolved.conll` as the held-out evaluation set.
2. Do not train directly on this gold test set if it will remain the final
   benchmark.
3. Add a small manually reviewed training set for weak labels, especially
   `DOSIS`, `OBAT`, and difficult `GEJALA` spans.
4. Add more challenge examples for lab/procedure/allergy labels before expanding
   the schema.
5. Keep evaluating every retraining run against `true_gold_300`.

## Key Artifacts

- Gold set: `data/true_gold_300/gold_resolved.conll`
- Agreement: `data/true_gold_300/agreement_summary.json`
- Adjudication notes: `data/true_gold_300/adjudication_notes.md`
- IndoBERT report: `reports/true_gold_300_indobert_report.md`
- Human-aligned IndoBERT report: `reports/true_gold_300_human_aligned_report.md`
- Human-aligned training report: `reports/human_aligned_training_summary.md`
- XLM-RoBERTa report: `reports/true_gold_300_xlm_roberta_report.md`
- True-gold comparison table: `reports/true_gold_300_model_comparison.md`
