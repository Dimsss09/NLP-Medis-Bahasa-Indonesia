# Tahap 2 — Assertion and Relation Extraction Evaluation Report

Generated at: Just now

## 🔍 Assertion Status Classification Performance
Kelas: `AFFIRMED`, `NEGATED`, `UNCERTAIN`

```text
              precision    recall  f1-score   support

    AFFIRMED       0.99      1.00      1.00       583
     NEGATED       0.91      0.91      0.91        11
   UNCERTAIN       1.00      0.79      0.88        14

    accuracy                           0.99       608
   macro avg       0.97      0.90      0.93       608
weighted avg       0.99      0.99      0.99       608

```

## 🔗 Relation Extraction Performance
Kelas: `dosage_of`, `treats`, `located_in`, `no_relation`

```text
              precision    recall  f1-score   support

   dosage_of       0.88      1.00      0.93         7
  located_in       0.98      0.99      0.99       267
 no_relation       0.82      0.67      0.74        21
      treats       0.92      0.96      0.94        23

    accuracy                           0.97       318
   macro avg       0.90      0.90      0.90       318
weighted avg       0.96      0.97      0.96       318

```

## 💡 Analisis Model Jangka Panjang
*   **Assertion Classifier** bekerja dengan sangat baik karena pola sintaksis penentu negasi ("tidak", "belum") dan ketidakpastian ("mungkin", "kemungkinan") dalam Bahasa Indonesia tergolong teratur dan konsisten.
*   **Relation Classifier** berhasil mempelajari asosiasi berpasangan dengan akurasi tinggi berkat penggunaan penanda entitas (`[START_HEAD]`, `[END_HEAD]`, dll.) yang memaksa model berfokus pada kandidat entitas yang sedang diuji.
