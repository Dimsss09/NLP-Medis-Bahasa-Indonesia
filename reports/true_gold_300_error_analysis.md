# Error Analysis

## Summary

- Micro F1: 0.3649
- Token accuracy: 0.6558
- Sentence exact match: 0.0733

## Main Failure Modes

- `OBAT` is under-predicted; recall is low despite high precision.
- The model is biased toward labels seen often in the bootstrap training subset.
- Metrics are measured against a manually adjudicated human gold set.

## Largest Token-Level Confusions

| Gold | Predicted | Count |
| --- | --- | ---: |
| B-GEJALA | O | 204 |
| I-GEJALA | O | 161 |
| B-OBAT | O | 136 |
| I-OBAT | O | 76 |
| B-DIAGNOSIS | O | 66 |
| B-ANATOMI | O | 64 |
| B-DIAGNOSIS | B-GEJALA | 14 |
| I-ANATOMI | O | 14 |
| I-DIAGNOSIS | O | 12 |
| O | B-DOSIS | 11 |

## Example Incorrect Predictions

- Text: apakah menstruasi berpengaruh pada rendahnya kadar hemoglobin
  Gold: O O O O B-GEJALA I-GEJALA I-GEJALA
  Pred: O O O O O O O
- Text: apakah batuk berkepanjangan dapat disembuhkan
  Gold: O B-GEJALA I-GEJALA O O
  Pred: O B-GEJALA O O O
- Text: cara mengatasi siku hingga telapak tangan bruntusan kecil dan terasa gatal
  Gold: O O B-ANATOMI O B-ANATOMI I-ANATOMI B-GEJALA I-GEJALA O O B-GEJALA
  Pred: O O O O B-ANATOMI I-ANATOMI B-GEJALA O O O B-GEJALA
- Text: keluar bercak coklat dan keputihan sebelum haid
  Gold: B-GEJALA I-GEJALA I-GEJALA O B-GEJALA O O
  Pred: O O O O O O O
- Text: tetes mata belekan di pagi hari yang bagus di apotek
  Gold: B-OBAT I-OBAT B-GEJALA O O O O O O O
  Pred: O B-ANATOMI O O O O O O O O

## Recommended Fixes

- Keep the true gold set held out as the benchmark.
- Add more manually validated `DOSIS`, `OBAT`, and `DIAGNOSIS` examples to training data.
- Correct a separate silver/human-aligned training subset using the adjudication rules.
- Retrain the NER model and evaluate again against the true gold set.
