# 11-Label Manual Boost Package

Generated at: 2026-06-16T14:22:41.152471+00:00

## Tujuan

Paket ini menambah contoh manual untuk 4 label yang masih lemah:
`RIWAYAT_PENYAKIT`, `DOSIS`, `PROSEDUR`, dan `WAKTU_DURASI`.

Label awal di file ini adalah draft otomatis. Dataset baru boleh disebut manual
gold setelah dua annotator manusia mengecek dan konflik diselesaikan manual.

## File

- `sample_texts.tsv`: daftar teks kandidat.
- `draft_labels.conll`: draft label awal.
- `annotator_1.conll`: file kerja annotator 1.
- `annotator_2.conll`: file kerja annotator 2.
- `human_review_status.tsv`: checklist progres review manusia.
- `MANUAL_REVIEW_GUIDE.md`: panduan singkat annotator.

## Jumlah contoh per fokus

- `RIWAYAT_PENYAKIT`: 50
- `DOSIS`: 50
- `PROSEDUR`: 50
- `WAKTU_DURASI`: 50

## Ringkasan label draft

- `B-ALERGI`: 5
- `B-ANATOMI`: 59
- `B-DIAGNOSIS`: 24
- `B-DOSIS`: 18
- `B-GEJALA`: 97
- `B-HASIL_LAB`: 1
- `B-NILAI_LAB`: 3
- `B-OBAT`: 107
- `B-PROSEDUR`: 50
- `B-RIWAYAT_PENYAKIT`: 49
- `B-WAKTU_DURASI`: 132
- `I-ALERGI`: 1
- `I-ANATOMI`: 2
- `I-GEJALA`: 46
- `I-HASIL_LAB`: 1
- `I-OBAT`: 10
- `I-PROSEDUR`: 27
- `I-RIWAYAT_PENYAKIT`: 26
- `I-WAKTU_DURASI`: 4

## Setelah annotator selesai

```powershell
.\venv\Scripts\python.exe src\annotation_agreement.py --manual-dir data\phase10_11label_manual_boost
```

Lalu isi konflik, kemudian:

```powershell
.\venv\Scripts\python.exe src\resolve_gold.py --manual-dir data\phase10_11label_manual_boost
```
