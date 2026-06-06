# Ekstraksi Informasi Otomatis dari Teks Medis Bahasa Indonesia

Proyek ini membangun sistem Named Entity Recognition (NER) untuk mengekstraksi
entitas medis dari teks Bahasa Indonesia. Entitas awal yang digunakan adalah
`GEJALA`, `OBAT`, `DOSIS`, `DIAGNOSIS`, dan `ANATOMI`.

## Tujuan

- Menyusun dataset medis Bahasa Indonesia dalam format BIO.
- Fine-tuning model IndoBERT untuk token classification.
- Mengukur precision, recall, dan F1 per entitas dengan `seqeval`.
- Menyediakan demo interaktif menggunakan Streamlit.

## Struktur Proyek

```text
data/
  raw/          data mentah
  clean/        data bersih
  annotated/    dataset BIO train/val/test
notebooks/      eksplorasi dan eksperimen
src/            skrip data, training, evaluasi, dan prediksi
models/         output model terlatih
reports/        metrik dan laporan evaluasi
app/            demo Streamlit
```

## Setup

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Menyiapkan Data

```powershell
python src/data_prep.py
```

Perintah ini mengambil dataset publik `iqbalpurba26/health-topic-dataset`,
menyimpan salinan JSONL ke `data/raw/`, lalu membuat korpus bersih siap anotasi
di `data/clean/medical_text_corpus.txt`.

## Membuat Anotasi BIO

```powershell
python src/annotate_bio.py
```

Perintah ini membuat anotasi awal berbasis lexicon dan aturan dosis, lalu
menyimpan split CoNLL/BIO ke `data/annotated/train.conll`,
`data/annotated/val.conll`, dan `data/annotated/test.conll`.

Catatan: label Fase 2 bersifat semi-otomatis dan perlu ditinjau manual sebelum
dipakai untuk klaim performa final.

## Melatih Model

```powershell
python src/train.py
```

Perintah ini melakukan fine-tuning `indobenchmark/indobert-base-p1` untuk token
classification dan menyimpan model ke `models/indobert-medical-ner-id`.
Konfigurasi awal memakai subset bootstrap agar training tetap realistis di CPU.

## Evaluasi Model

```powershell
python src/evaluate.py
```

Perintah ini menghitung precision, recall, dan F1 per entitas dengan `seqeval`,
menyimpan confusion matrix, dan menulis contoh prediksi ke folder `reports/`.

## Validasi Manual Mendekati Industri

```powershell
python src/prepare_manual_gold.py
python src/annotation_agreement.py
python src/resolve_gold.py
python src/evaluate.py --test-file data/manual_gold/gold_resolved.conll --report-prefix gold
python src/error_analysis.py
```

`prepare_manual_gold.py` menyiapkan 400 kalimat untuk dua annotator. File
annotator harus diisi manusia secara independen sebelum agreement, gold
resolution, dan evaluasi gold dapat dianggap valid.

## Menjalankan Demo

```powershell
streamlit run app/demo.py
```

Untuk saat ini demo masih berupa shell awal. Inferensi akan diaktifkan setelah
fase training selesai.

## Status Roadmap

- [x] Fase 0 - Inisialisasi proyek
- [x] Fase 1 - Pengumpulan dan pembersihan data
- [x] Fase 2 - Anotasi data format BIO
- [x] Fase 3 - Fine-tuning model
- [x] Fase 4 - Evaluasi
- [ ] Fase 5 - Demo interaktif
- [ ] Fase 6 - Dokumentasi dan finalisasi
