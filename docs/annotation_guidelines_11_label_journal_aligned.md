# Panduan Anotasi 11 Label - Selaras Literatur Klinis/Farmasi

Dokumen ini menjadi pegangan untuk menaikkan proyek dari 5 label ke 11 label.
Bahasanya dibuat praktis agar annotator non-IT tetap bisa menggunakannya.

## Sumber Standar yang Dipakai

Panduan ini diringkas dari pola umum benchmark dan korpus klinis/farmasi:

- i2b2/VA 2010 concept annotation: membedakan konsep klinis menjadi problem,
  treatment, dan test.
- n2c2 2018 ADE/Medication Extraction: menandai obat dan atribut obat seperti
  dosage, duration, route, frequency, reason, dan ADE.
- CADEC: korpus farmakovigilans yang menandai drugs, adverse effects, symptoms,
  dan diseases dengan anotasi bertahap, agreement, dan review klinis.
- Literatur medication extraction: informasi obat biasanya tidak cukup hanya
  nama obat, tetapi juga dosis, frekuensi, rute, durasi, dan konteks terapi.

## Prinsip Umum

1. Tandai span yang paling bermakna secara klinis.
2. Jangan menandai kata kerja umum jika bukan bagian penting entitas.
3. Gunakan `B-` untuk kata pertama entitas dan `I-` untuk lanjutan.
4. Kalau dua entitas berbeda berdampingan, pisahkan.
5. Kalau ragu, pilih label yang menjawab fungsi klinis kata tersebut.

Contoh:

```text
riwayat B-RIWAYAT_PENYAKIT
diabetes I-RIWAYAT_PENYAKIT
dan I-RIWAYAT_PENYAKIT
asma I-RIWAYAT_PENYAKIT
```

```text
operasi B-PROSEDUR
caesar I-PROSEDUR
```

```text
gula B-HASIL_LAB
darah I-HASIL_LAB
tinggi B-NILAI_LAB
```

## Definisi 11 Label

| Label | Dipakai untuk | Contoh |
| --- | --- | --- |
| `GEJALA` | keluhan/tanda klinis | gatal, nyeri perut, sesak napas |
| `OBAT` | obat, zat terapi, alat terapi, produk perawatan | paracetamol, cetirizine, nebulizer |
| `DOSIS` | jumlah, kekuatan, bentuk, frekuensi, aturan pakai | 500 mg, 2 kali sehari, tablet, sirup |
| `DIAGNOSIS` | penyakit/kondisi medis | diabetes, wasir, keloid, hipertensi |
| `ANATOMI` | bagian tubuh | kulit, paru-paru, mata, perut bawah |
| `PROSEDUR` | tindakan/intervensi/pemeriksaan | operasi caesar, USG, rontgen, vaksinasi, suntik KB |
| `HASIL_LAB` | nama parameter lab/pemeriksaan penunjang | leukosit, trombosit, gula darah, kolesterol |
| `NILAI_LAB` | nilai/status hasil | tinggi, rendah, negatif, positif, normal |
| `WAKTU_DURASI` | waktu/lama/frekuensi/tanggal relatif | 3 hari, 2 minggu, pagi hari, tahun |
| `ALERGI` | kondisi/reaksi/jenis alergi | alergi, alergi debu, alergi obat |
| `RIWAYAT_PENYAKIT` | penyakit/kondisi yang eksplisit disebut sebagai riwayat | riwayat TB, riwayat diabetes |

## Aturan Khusus Label Lemah

### RIWAYAT_PENYAKIT

Tandai hanya jika ada penanda riwayat yang jelas, misalnya `riwayat`,
`pernah menderita`, `memiliki riwayat`, atau pola serupa.

```text
riwayat B-RIWAYAT_PENYAKIT
tb I-RIWAYAT_PENYAKIT
```

Kalau hanya nama penyakit tanpa penanda riwayat, pakai `DIAGNOSIS`.

```text
diabetes B-DIAGNOSIS
```

### DOSIS

Ikuti pendekatan medication extraction: dosis tidak hanya angka, tetapi juga
kekuatan, bentuk, frekuensi, dan aturan pakai obat bila tertulis.

```text
500 B-DOSIS
mg I-DOSIS
```

```text
2 B-DOSIS
kali I-DOSIS
sehari I-DOSIS
```

```text
tablet B-DOSIS
```

### PROSEDUR

Ikuti konsep treatment/test: tindakan, intervensi, tes, pemeriksaan, operasi,
vaksinasi, dan suntikan sebagai tindakan.

```text
pemeriksaan B-PROSEDUR
usg I-PROSEDUR
```

```text
vaksinasi B-PROSEDUR
covid I-PROSEDUR
```

### WAKTU_DURASI

Tandai ekspresi waktu yang benar-benar menyatakan lama, waktu, frekuensi, atau
tanggal relatif. Untuk aturan sementara proyek ini, satuan usia seperti `tahun`
dan `bulan` tetap ditandai `WAKTU_DURASI`.

```text
selama B-WAKTU_DURASI
3 I-WAKTU_DURASI
hari I-WAKTU_DURASI
```

```text
usia O
2 O
tahun B-WAKTU_DURASI
```

Kata penghubung seperti `setelah` atau `pasca` tidak perlu ditandai jika berdiri
sendiri tanpa ekspresi waktu yang jelas.

## Konflik yang Perlu Diingat

- `alergi` -> `ALERGI`, kecuali menempel langsung pada frasa `riwayat alergi`,
  maka boleh menjadi bagian `RIWAYAT_PENYAKIT`.
- `vaksin`, `vaksinasi`, `divaksin` -> `PROSEDUR`.
- `kolesterol tinggi` -> `kolesterol` sebagai `HASIL_LAB`, `tinggi` sebagai
  `NILAI_LAB`.
- `obat cacing` -> `obat cacing` sebagai `OBAT`, bukan diagnosis.
- `mabuk perjalanan` -> `GEJALA`.
