# Error Analysis

## Summary

- Micro F1: 0.5137
- Token accuracy: 0.6859
- Sentence exact match: 0.0563

## Main Failure Modes

- The model did not predict any `B-DOSIS` labels, so dosage recall is zero.
- `OBAT` is under-predicted; recall is low despite high precision.
- The model is biased toward labels seen often in the bootstrap training subset.
- Metrics are measured against a manually adjudicated human gold set.

## Largest Token-Level Confusions

| Gold | Predicted | Count |
| --- | --- | ---: |
| B-GEJALA | O | 50 |
| B-PROSEDUR | O | 41 |
| B-WAKTU_DURASI | O | 39 |
| B-ALERGI | B-DIAGNOSIS | 33 |
| I-GEJALA | O | 27 |
| I-PROSEDUR | O | 26 |
| I-RIWAYAT_PENYAKIT | O | 22 |
| B-RIWAYAT_PENYAKIT | O | 20 |
| B-HASIL_LAB | O | 19 |
| B-DIAGNOSIS | O | 18 |

## Example Incorrect Predictions

- Text: obat yang bagus untuk mengatasi gula darah tinggi
  Gold: B-OBAT O O O O B-HASIL_LAB I-HASIL_LAB B-NILAI_LAB
  Pred: B-OBAT O O O O O O O
- Text: telat haid testpack negatif pinggang sakit keluar flek coklat dan urine berdarah
  Gold: B-GEJALA I-GEJALA B-PROSEDUR B-NILAI_LAB B-ANATOMI B-GEJALA B-GEJALA I-GEJALA I-GEJALA O B-GEJALA I-GEJALA
  Pred: B-GEJALA I-GEJALA O O O B-GEJALA B-GEJALA I-GEJALA I-GEJALA O O B-GEJALA
- Text: rekomendasi obat untuk mengatasi leher tegang karena kolesterol
  Gold: O B-OBAT O O B-ANATOMI B-GEJALA O B-HASIL_LAB
  Pred: O B-OBAT O O B-ANATOMI O O O
- Text: obat untuk menurunkan kadar gula darah tinggi sampai
  Gold: B-OBAT O O O B-HASIL_LAB I-HASIL_LAB B-NILAI_LAB O
  Pred: B-OBAT O O O O O O O
- Text: bolehkan konsumsi obat kolesterol tanpa cek darah
  Gold: O O B-OBAT B-HASIL_LAB O B-PROSEDUR I-PROSEDUR
  Pred: O O B-OBAT O O O O

## Recommended Fixes

- Keep the true gold set held out as the benchmark.
- Add more manually validated `DOSIS`, `OBAT`, and `DIAGNOSIS` examples to training data.
- Correct a separate silver/human-aligned training subset using the adjudication rules.
- Retrain the NER model and evaluate again against the true gold set.
