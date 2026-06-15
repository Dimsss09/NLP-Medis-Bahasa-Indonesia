# Catatan Penyelesaian Konflik True Gold 300

Tanggal: 2026-06-15
Folder data: `data/true_gold_300`
Jumlah teks: 300
Jumlah token: 2403
Jumlah konflik label: 263

## Ringkasan Agreement

- Status: ready_for_resolution
- Token agreement: 0.8906
- Cohen's Kappa: 0.8290
- Entity F1 antar annotator: 0.7532

Makna sederhana: dua annotator sudah cukup konsisten untuk tahap prototype
riset, tetapi masih ada 263 perbedaan label yang harus diputuskan manual.

## File yang Harus Direview

Isi kolom `resolved_label` di file:

```text
data/true_gold_300/conflicts.tsv
```

File tersebut sudah ditambahkan kolom `sentence_text`, supaya reviewer bisa
melihat kalimat lengkap saat memilih label final.

## Aturan Penyelesaian

- Baca kalimat lengkap sebelum memilih label final.
- Jangan memilih otomatis hanya karena salah satu annotator.
- Jika token memang bukan entitas medis, isi `resolved_label` dengan `O`.
- Jika token adalah awal entitas, isi dengan `B-LABEL`.
- Jika token adalah lanjutan entitas yang sama, isi dengan `I-LABEL`.
- Gunakan label yang tersedia saja: `GEJALA`, `OBAT`, `DOSIS`, `DIAGNOSIS`,
  dan `ANATOMI`.

## Prinsip Adjudikasi yang Dipakai

| Tipe entitas | Pegangan keputusan |
| --- | --- |
| `ANATOMI` | Bagian tubuh selalu menjadi entitas sendiri. Pada pola bagian tubuh + gejala, seperti `hidung tersumbat`, `mata bengkak`, atau `sakit gigi`, bagian tubuh diberi `ANATOMI` dan keluhannya diberi `GEJALA`. |
| `GEJALA` | Kata keluhan atau temuan klinis seperti `gatal`, `nyeri`, `perih`, `bengkak`, `tersumbat`, dan `berdarah`. Kata kerja atau penghubung seperti `terasa`, `muncul`, `timbul`, `keluar`, `sering`, dan `selalu` diberi `O`. |
| `DIAGNOSIS` | Kondisi atau penyakit bernama, seperti `biduran`, `bisul`, `trikomoniasis`, `panas dalam`, `kolesterol tinggi`, `floaters`, `purging`, `breakout`, `flek paru`, `hamil`, dan `kehamilan`. |
| `OBAT` | Nama, zat, atau produk terapi, termasuk produk topikal atau kosmetik seperti `asam mefenamat`, `imunosupresan`, `salep mata`, `air alkali`, `sabun wajah`, `handbody`, `softlens`, dan `masker kopi`. Modifier nama obat menjadi `I-OBAT`. |
| `DOSIS` | Bentuk sediaan sebagai penanda, misalnya `sirup` dan `kapsul`. |

Keputusan khusus:

- `hamil` dan `kehamilan` dikonsistenkan sebagai `B-DIAGNOSIS`.
- `kandungan` bergantung konteks: `periksa kandungan` sebagai rahim diberi
  `B-ANATOMI`, sedangkan `kandungan obat/zat` sebagai komposisi diberi `O`.
- `panas dalam`, `kolesterol tinggi`, `infeksi trikomoniasis`, dan `uterus
  retrofleksi membesar` diberi span `DIAGNOSIS`.
- Pola seperti `tidak teratur` atau `tidak lancar` pada siklus haid diberi
  `GEJALA`.
- Frasa majemuk seperti `air mata`, `bulu kaki`, dan `mata kanan` dijaga utuh
  sebagai `B-` lalu `I-`, bukan dipecah.

Distribusi label final pada konflik:

| Label final | Jumlah |
| --- | ---: |
| `B-GEJALA` | 68 |
| `O` | 65 |
| `B-ANATOMI` | 38 |
| `B-DIAGNOSIS` | 34 |
| `I-GEJALA` | 21 |
| `I-OBAT` | 18 |
| `B-OBAT` | 6 |
| `I-DIAGNOSIS` | 6 |
| `I-ANATOMI` | 4 |
| `B-DOSIS` | 3 |

## Contoh Cara Mengisi

Jika konflik seperti ini:

```text
token: gatal
annotator_1: I-GEJALA
annotator_2: B-GEJALA
```

Pilih:

- `B-GEJALA` kalau `gatal` adalah awal gejala baru.
- `I-GEJALA` kalau `gatal` adalah lanjutan dari frasa gejala sebelumnya.

## Catatan Keterbatasan

- Dataset ini adalah human-annotated gold set untuk evaluasi prototype.
- Dataset ini belum boleh disebut validasi klinis formal.
- Konflik yang membingungkan secara medis sebaiknya dicek lagi oleh orang yang
  lebih paham konteks kesehatan.

## Setelah Semua Konflik Selesai

Semua konflik sudah diselesaikan di:

```text
data/true_gold_300/conflicts_resolved.tsv
```

File final gold sudah dibuat:

```text
data/true_gold_300/gold_resolved.conll
```

Evaluasi true gold sudah dijalankan dengan:

```powershell
.\venv\Scripts\python.exe src\evaluate.py --test-file data\true_gold_300\gold_resolved.conll --report-prefix true_gold_300
```
