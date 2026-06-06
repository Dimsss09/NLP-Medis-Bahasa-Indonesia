# Error Analysis

## Summary

- Micro F1: 0.9659
- Token accuracy: 0.9931
- Sentence exact match: 0.9609

## Main Failure Modes

- `OBAT` still has a small number of missed mentions despite high overall recall.
- The model is biased toward labels seen often in the bootstrap training subset.
- Metrics are still measured against semi-automatic labels, not a human gold set.

## Largest Token-Level Confusions

| Gold | Predicted | Count |
| --- | --- | ---: |
| O | B-GEJALA | 15 |
| B-GEJALA | B-ANATOMI | 14 |
| I-GEJALA | O | 10 |
| O | I-DOSIS | 6 |
| I-GEJALA | B-GEJALA | 6 |
| B-DIAGNOSIS | O | 5 |
| O | B-ANATOMI | 3 |
| B-GEJALA | O | 3 |
| O | B-DOSIS | 2 |
| B-OBAT | O | 2 |

## Example Incorrect Predictions

- Text: badan anak usia bulan bengkakbengkak hingga kepala
  Gold: B-ANATOMI O O O O O B-ANATOMI
  Pred: B-ANATOMI O O O B-GEJALA O B-ANATOMI
- Text: efek samping obat ibuprofen
  Gold: O O O B-OBAT
  Pred: O O O O
- Text: timbul bintik merah pada bayi menyusu setelah ibu makan ikan laut
  Gold: O B-GEJALA I-GEJALA O O O O O O O O
  Pred: O B-GEJALA I-GEJALA O O O B-DOSIS O I-DOSIS O O
- Text: bintik kemerahan pada kulit dan disertai dengan gatal
  Gold: O O O B-ANATOMI O O O B-GEJALA
  Pred: B-GEJALA O O B-ANATOMI O O O B-GEJALA
- Text: sakit perut bagian kiri saat minum obat untuk luka jahit pada jari
  Gold: B-GEJALA I-GEJALA O O O O O O O O O O
  Pred: B-GEJALA I-GEJALA O O O I-DOSIS O O O O O O

## Recommended Fixes

- Complete manual double annotation and evaluate on `gold_resolved.conll`.
- Add more manually validated `DOSIS` and `OBAT` examples to training.
- Train on a larger subset or full training set when GPU time is available.
- Review ambiguous lexicon labels before reporting final performance.
