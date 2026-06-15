# Panduan Singkat untuk Annotator

Tugas kamu adalah membaca teks medis pendek dan memberi label pada kata-kata
penting.

Jangan mengubah kata. Jangan menghapus baris. Jangan menambah baris.

Yang diubah hanya label di sebelah kanan kata.

## File yang Dikerjakan

Annotator 1 mengerjakan:

```text
annotator_1.conll
```

Annotator 2 mengerjakan:

```text
annotator_2.conll
```

Kerjakan file masing-masing. Jangan melihat file annotator lain sebelum selesai.

## Label yang Dipakai

| Label | Arti | Contoh |
| --- | --- | --- |
| `GEJALA` | keluhan pasien | demam, batuk, gatal, nyeri dada |
| `OBAT` | nama obat atau jenis obat | paracetamol, amoxicillin, insulin |
| `DOSIS` | jumlah atau aturan pakai obat | 500 mg, 3x sehari, selama 5 hari |
| `DIAGNOSIS` | penyakit atau kondisi medis | diabetes, asma, hipertensi |
| `ANATOMI` | bagian tubuh | kepala, dada, kulit, tangan |

## Cara Memberi Label

Kalau kata bukan bagian penting medis, biarkan:

```text
O
```

Kalau kata adalah bagian penting medis, pakai:

```text
B-LABEL
```

Kalau bagian pentingnya terdiri dari beberapa kata, kata pertama pakai `B-`,
kata berikutnya pakai `I-`.

Contoh:

```text
Pasien O
mengalami O
demam B-GEJALA
tinggi I-GEJALA
```

Contoh:

```text
Pasien O
minum O
paracetamol B-OBAT
500 B-DOSIS
mg I-DOSIS
```

Contoh:

```text
Pasien O
diabetes B-DIAGNOSIS
dan O
nyeri B-GEJALA
pada O
kaki B-ANATOMI
```

## Jika Bingung

Pilih label yang menurutmu paling masuk akal berdasarkan kalimat.

Tidak apa-apa kalau jawabanmu berbeda dari annotator lain. Perbedaan itu nanti
akan dicek dan diputuskan secara manual.

Panduan lebih lengkap ada di:

```text
docs/true_gold_dataset_workflow.md
```
