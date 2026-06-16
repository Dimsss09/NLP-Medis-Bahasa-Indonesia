# Error Analysis

## Summary

- Micro F1: 0.6837
- Token accuracy: 0.7716
- Sentence exact match: 0.2000

## Main Failure Modes

- The model did not predict any `B-DOSIS` labels, so dosage recall is zero.
- `OBAT` is under-predicted; recall is low despite high precision.
- The model is biased toward labels seen often in the bootstrap training subset.
- Metrics are measured against a manually adjudicated human gold set.

## Largest Token-Level Confusions

| Gold | Predicted | Count |
| --- | --- | ---: |
| B-GEJALA | O | 49 |
| O | B-WAKTU_DURASI | 45 |
| I-GEJALA | O | 27 |
| I-RIWAYAT_PENYAKIT | O | 21 |
| B-RIWAYAT_PENYAKIT | O | 18 |
| B-DIAGNOSIS | O | 17 |
| B-OBAT | O | 14 |
| I-OBAT | O | 12 |
| B-PROSEDUR | O | 10 |
| B-ANATOMI | O | 9 |

## Example Incorrect Predictions

- Text: telat haid testpack negatif pinggang sakit keluar flek coklat dan urine berdarah
  Gold: B-GEJALA I-GEJALA B-PROSEDUR B-NILAI_LAB B-ANATOMI B-GEJALA B-GEJALA I-GEJALA I-GEJALA O B-GEJALA I-GEJALA
  Pred: B-GEJALA I-GEJALA O O O B-GEJALA B-GEJALA I-GEJALA I-GEJALA O B-HASIL_LAB B-GEJALA
- Text: rekomendasi obat untuk mengatasi leher tegang karena kolesterol
  Gold: O B-OBAT O O B-ANATOMI B-GEJALA O B-HASIL_LAB
  Pred: O B-OBAT O O B-ANATOMI O O B-HASIL_LAB
- Text: obat untuk mengatasi mata kaki bengkak karena asam urat
  Gold: B-OBAT O O B-ANATOMI I-ANATOMI B-GEJALA O B-HASIL_LAB I-HASIL_LAB
  Pred: B-OBAT O O B-ANATOMI B-ANATOMI B-GEJALA O B-HASIL_LAB I-HASIL_LAB
- Text: obat untuk mengatasi peningkatan sgpt dan asam urat
  Gold: B-OBAT O O B-NILAI_LAB B-HASIL_LAB O B-HASIL_LAB I-HASIL_LAB
  Pred: B-OBAT O O B-NILAI_LAB O O B-HASIL_LAB I-HASIL_LAB
- Text: bolehkah konsumsi obat kolesterol darah tinggi dan asam urat bersamaan dengan vitamin d
  Gold: O O B-OBAT B-HASIL_LAB I-HASIL_LAB B-NILAI_LAB O B-HASIL_LAB I-HASIL_LAB O O B-OBAT I-OBAT
  Pred: O O B-OBAT B-HASIL_LAB O B-NILAI_LAB O B-HASIL_LAB I-HASIL_LAB O O B-OBAT O

## Recommended Fixes

- Keep the true gold set held out as the benchmark.
- Add more manually validated `DOSIS`, `OBAT`, and `DIAGNOSIS` examples to training data.
- Correct a separate silver/human-aligned training subset using the adjudication rules.
- Retrain the NER model and evaluate again against the true gold set.
