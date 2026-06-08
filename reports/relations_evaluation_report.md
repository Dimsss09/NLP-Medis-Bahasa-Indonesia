# Tahap 2 — Assertion and Relation Extraction Evaluation Report

Generated at: 1780877609.552222

## 🔍 Assertion Status Classification Performance
Kelas: `AFFIRMED`, `NEGATED`, `UNCERTAIN`

```text
              precision    recall  f1-score   support

    AFFIRMED       0.99      1.00      1.00       595
     NEGATED       0.91      0.91      0.91        11
   UNCERTAIN       1.00      0.79      0.88        14

    accuracy                           0.99       620
   macro avg       0.97      0.90      0.93       620
weighted avg       0.99      0.99      0.99       620

```

## 🔗 Relation Extraction Performance
Kelas: `dosage_of`, `treats`, `located_in`, `no_relation`

```text
              precision    recall  f1-score   support

   dosage_of       1.00      1.00      1.00         7
  located_in       0.99      0.99      0.99       275
 no_relation       0.90      0.90      0.90        21
      treats       1.00      1.00      1.00        23

    accuracy                           0.99       326
   macro avg       0.97      0.97      0.97       326
weighted avg       0.99      0.99      0.99       326

```

## 💡 Analisis Model Jangka Panjang
*   **Assertion Classifier** bekerja dengan sangat baik karena pola sintaksis penentu negasi ("tidak", "belum") dan ketidakpastian ("mungkin", "kemungkinan") dalam Bahasa Indonesia tergolong teratur dan konsisten.
*   **Relation Classifier** berhasil mempelajari asosiasi berpasangan dengan akurasi tinggi berkat penggunaan penanda entitas (`[START_HEAD]`, `[END_HEAD]`, dll.) yang memaksa model berfokus pada kandidat entitas yang sedang diuji.
