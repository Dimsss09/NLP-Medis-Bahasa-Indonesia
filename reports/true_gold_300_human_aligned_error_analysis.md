# Error Analysis

## Summary

- Micro F1: 0.7238
- Token accuracy: 0.8419
- Sentence exact match: 0.3800

## Main Failure Modes

- `OBAT` is under-predicted; recall is low despite high precision.
- The model is biased toward labels seen often in the bootstrap training subset.
- Metrics are measured against a manually adjudicated human gold set.

## Largest Token-Level Confusions

| Gold | Predicted | Count |
| --- | --- | ---: |
| B-GEJALA | O | 94 |
| I-GEJALA | O | 88 |
| I-OBAT | O | 44 |
| B-OBAT | O | 24 |
| B-DIAGNOSIS | O | 20 |
| B-ANATOMI | O | 20 |
| I-GEJALA | B-GEJALA | 13 |
| I-OBAT | B-ANATOMI | 10 |
| I-OBAT | B-OBAT | 7 |
| I-DIAGNOSIS | O | 7 |

## Example Incorrect Predictions

- Text: apakah menstruasi berpengaruh pada rendahnya kadar hemoglobin
  Gold: O O O O B-GEJALA I-GEJALA I-GEJALA
  Pred: O O O O O O O
- Text: cara mengatasi siku hingga telapak tangan bruntusan kecil dan terasa gatal
  Gold: O O B-ANATOMI O B-ANATOMI I-ANATOMI B-GEJALA I-GEJALA O O B-GEJALA
  Pred: O O B-ANATOMI O B-ANATOMI I-ANATOMI B-GEJALA O O O B-GEJALA
- Text: tetes mata belekan di pagi hari yang bagus di apotek
  Gold: B-OBAT I-OBAT B-GEJALA O O O O O O O
  Pred: B-DOSIS B-ANATOMI O O O O O O O O
- Text: kulit wajah memerah terasa kaku seperti plastik dan perih tetapi tidak gatal
  Gold: B-ANATOMI I-ANATOMI B-GEJALA O B-GEJALA O O O B-GEJALA O B-GEJALA I-GEJALA
  Pred: B-ANATOMI I-ANATOMI O O B-GEJALA O O O O O O B-GEJALA
- Text: kemungkinan keguguran saat vagina keluar darah menggumpal
  Gold: O B-DIAGNOSIS O B-ANATOMI B-GEJALA I-GEJALA I-GEJALA
  Pred: O B-DIAGNOSIS O B-ANATOMI B-GEJALA I-GEJALA O

## Recommended Fixes

- Keep the true gold set held out as the benchmark.
- Add more manually validated `DOSIS`, `OBAT`, and `DIAGNOSIS` examples to training data.
- Correct a separate silver/human-aligned training subset using the adjudication rules.
- Retrain the NER model and evaluate again against the true gold set.
