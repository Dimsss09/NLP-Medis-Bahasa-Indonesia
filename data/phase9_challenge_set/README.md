# Phase 9 Challenge Set

Generated at: 2026-06-15T09:13:17.442260+00:00

## Tujuan

Folder ini berisi 160 kandidat teks untuk memperkuat benchmark proyek.
Fokusnya adalah kasus yang lebih sulit: dosis, obat, gejala, alergi, prosedur,
hasil lab, nilai lab, waktu/durasi, dan riwayat penyakit.

## Status penting

File ini belum boleh disebut gold dataset. Label awal dibuat otomatis sebagai
draft bantuan. Dataset baru boleh disebut manual/gold setelah manusia mengecek
labelnya dan konflik diselesaikan manual.

## File

- `sample_texts.tsv`: daftar teks yang dipilih.
- `draft_labels.conll`: label awal dari aturan/AI, hanya untuk bantuan review.
- `annotator_1.conll`: salinan draft untuk dikoreksi annotator 1.
- `annotator_2.conll`: salinan draft untuk dikoreksi annotator 2.
- `labels.txt`: daftar label yang boleh dipakai.
- `human_review_status.tsv`: checklist sederhana agar tahu mana yang sudah dicek.
- `adjudication_notes.md`: tempat mencatat keputusan konflik.

## Cara kerja

1. Annotator 1 membuka `annotator_1.conll` dan mengoreksi label yang salah.
2. Annotator 2 membuka `annotator_2.conll` dan mengoreksi label secara terpisah.
3. Tandai progres di `human_review_status.tsv`.
4. Jalankan agreement:

```powershell
.\venv\Scripts\python.exe src\annotation_agreement.py --manual-dir data\phase9_challenge_set
```

5. Isi `conflicts.tsv` pada kolom `resolved_label`.
6. Jalankan resolve:

```powershell
.\venv\Scripts\python.exe src\resolve_gold.py --manual-dir data\phase9_challenge_set
```

## Ringkasan fokus teks

- `ALERGI`: 34
- `GEJALA_SULIT`: 50
- `HASIL_LAB`: 23
- `OBAT_DOSIS`: 74
- `PROSEDUR`: 39
- `RIWAYAT_PENYAKIT`: 23
- `WAKTU_DURASI`: 71

## Ringkasan label draft

- `B-ALERGI`: 33
- `B-ANATOMI`: 59
- `B-DIAGNOSIS`: 22
- `B-GEJALA`: 95
- `B-HASIL_LAB`: 24
- `B-NILAI_LAB`: 12
- `B-OBAT`: 83
- `B-PROSEDUR`: 42
- `B-RIWAYAT_PENYAKIT`: 3
- `B-WAKTU_DURASI`: 77
- `I-ALERGI`: 1
- `I-ANATOMI`: 4
- `I-GEJALA`: 20
- `I-HASIL_LAB`: 10
- `I-OBAT`: 11
- `I-PROSEDUR`: 24
- `I-RIWAYAT_PENYAKIT`: 3
- `I-WAKTU_DURASI`: 1

## Aturan tambahan label baru

- `ALERGI`: kondisi alergi atau jenis alerginya, misalnya alergi debu.
- `PROSEDUR`: tindakan atau pemeriksaan, misalnya operasi caesar, rontgen, USG, vaksin.
- `HASIL_LAB`: nama pemeriksaan/parameter lab, misalnya leukosit, hemoglobin, gula darah.
- `NILAI_LAB`: nilai atau status hasil lab, misalnya tinggi, rendah, normal.
- `WAKTU_DURASI`: waktu atau lama keluhan, misalnya hari, minggu, bulan, pagi hari.
- `RIWAYAT_PENYAKIT`: riwayat kondisi sebelumnya, misalnya riwayat TB atau riwayat alergi.
