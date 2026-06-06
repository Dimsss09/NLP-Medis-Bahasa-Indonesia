# Ekstraksi Informasi Otomatis dari Teks Medis Bahasa Indonesia

![Python](https://img.shields.io/badge/Python-3.12-blue)
![Model](https://img.shields.io/badge/Model-IndoBERT-teal)
![Demo](https://img.shields.io/badge/Demo-Streamlit-ff4b4b)
![Micro F1](https://img.shields.io/badge/Silver%20Micro%20F1-0.9659-brightgreen)
![Status](https://img.shields.io/badge/Phase%206-Finalized-success)

Proyek ini membangun sistem Named Entity Recognition (NER) untuk mengekstraksi
entitas medis dari teks Bahasa Indonesia. Entitas yang dikenali saat ini adalah
`GEJALA`, `OBAT`, `DOSIS`, `DIAGNOSIS`, dan `ANATOMI`.

Output utama proyek:

- pipeline data dari korpus mentah ke format BIO/CoNLL;
- dataset silver berbasis rules dan lexicon;
- fine-tuned IndoBERT untuk token classification;
- laporan evaluasi, error analysis, dan model card;
- demo lokal Streamlit dengan highlight entitas berwarna.

## Hasil Singkat

Evaluasi engineering terbaru dijalankan pada test set semi-otomatis/silver, jadi
angka ini berguna untuk melihat progres model tetapi belum boleh dianggap
sebagai klaim performa klinis final.

| Metrik | Nilai |
| --- | ---: |
| Sentences | 1,306 |
| Tokens | 10,337 |
| Token accuracy | 0.9931 |
| Sentence exact match | 0.9609 |
| Micro precision | 0.9556 |
| Micro recall | 0.9765 |
| Micro F1 | 0.9659 |

Detail lengkap tersedia di `reports/evaluation_report.md`,
`reports/evaluation_metrics.json`, dan `reports/error_analysis.md`.

## Screenshot Evidence

Screenshot berikut diambil dari demo Streamlit lokal setelah model berhasil
memuat dan mengekstraksi entitas dari contoh teks medis.

![Demo Streamlit Medical NER](docs/screenshots/demo_phase6_streamlit.png)

## Cara Instal

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Model hasil training disimpan secara lokal di
`models/indobert-medical-ner-id`. Folder `models/` tidak dikomit karena berisi
file bobot besar.

## Cara Jalankan Demo

```powershell
streamlit run app/demo.py
```

Jika memakai konfigurasi lokal dari repo ini, Streamlit akan berjalan di:

```text
http://localhost:8501
```

Cara pakai demo:

1. Buka halaman Streamlit.
2. Pastikan `Model directory` mengarah ke `models/indobert-medical-ner-id`.
3. Masukkan teks medis Bahasa Indonesia.
4. Klik `Ekstrak Entitas`.
5. Lihat hasil sorotan, tabel entitas, dan tabel token.

Contoh teks:

```text
Pasien mengalami demam tinggi, nyeri dada, dan minum paracetamol 500 mg sesudah makan.
```

Contoh output yang diharapkan:

| Entitas | Label |
| --- | --- |
| demam | GEJALA |
| nyeri | GEJALA |
| dada | ANATOMI |
| paracetamol | OBAT |
| sesudah makan | DOSIS |

## Cara Pakai dari Script

Prediksi juga bisa dijalankan tanpa UI:

```powershell
python src/predict.py "Pasien batuk pilek dan diberi amoxicillin 500 mg dua kali sehari."
```

Perintah tersebut memuat model lokal, menjalankan inference, lalu menampilkan
token dan span entitas yang terdeteksi.

## Model

Model dasar yang digunakan adalah `indobenchmark/indobert-base-p1`, lalu
di-fine-tune sebagai token classification model. Pipeline training membaca data
BIO/CoNLL, menyelaraskan token label dengan subword tokenizer IndoBERT, lalu
menyimpan tokenizer, konfigurasi label, dan bobot model ke
`models/indobert-medical-ner-id`.

Label NER:

| Label | Makna |
| --- | --- |
| `GEJALA` | gejala atau keluhan pasien |
| `OBAT` | nama obat atau zat terapi |
| `DOSIS` | aturan pakai, frekuensi, jumlah, atau waktu konsumsi |
| `DIAGNOSIS` | nama penyakit atau kondisi medis |
| `ANATOMI` | bagian tubuh atau organ |

Strategi data saat ini memakai `data/silver/` sebagai training source. Silver
annotation dibuat dari rules dan lexicon sehingga cocok untuk bootstrap model,
tetapi bukan pengganti human gold. Workflow human gold sudah disiapkan di
`data/manual_gold/` dan perlu diisi oleh minimal dua annotator manusia sebelum
agreement, conflict resolution, dan evaluasi final berbasis gold test set.

## Tech Web Demo

Demo interaktif dibangun dengan Streamlit di `app/demo.py`.

Komponen teknis:

- Streamlit untuk UI lokal, text area, tombol inference, sidebar model path, dan
  tabel hasil.
- PyTorch dan Hugging Face Transformers untuk memuat tokenizer serta model
  IndoBERT token classification.
- CSS custom untuk background medical NLP, logo animasi, panel hasil, dan badge
  highlight entitas.
- Asset visual lokal di `assets/medical-ner-background.png`, di-embed sebagai
  data URI agar demo tetap berjalan tanpa server asset tambahan.

## Pipeline Proyek

### 1. Menyiapkan Data

```powershell
python src/data_prep.py
```

Mengambil dataset publik `iqbalpurba26/health-topic-dataset`, menyimpan salinan
JSONL ke `data/raw/`, lalu membuat korpus bersih di
`data/clean/medical_text_corpus.txt`.

### 2. Membuat Anotasi BIO

```powershell
python src/annotate_bio.py
```

Membuat anotasi awal berbasis lexicon dan aturan dosis ke
`data/annotated/train.conll`, `data/annotated/val.conll`, dan
`data/annotated/test.conll`.

### 3. Membuat Silver Dataset

```powershell
python src/build_silver_dataset.py
```

Membuat dataset `data/silver/` dari rules dan lexicon. Silver data boleh
dipakai untuk memperbesar training, tetapi tidak boleh dilaporkan sebagai human
gold atau bukti agreement annotator.

### 4. Melatih Model

```powershell
python src/train.py
```

Melakukan fine-tuning IndoBERT dan menyimpan output ke
`models/indobert-medical-ner-id`. Konfigurasi training berada di `config.yaml`;
saat ini `training.train_data_source` disetel ke `silver`.

### 5. Evaluasi Model

```powershell
python src/evaluate.py
```

Menghitung precision, recall, F1 dengan `seqeval`, menyimpan confusion matrix,
dan menulis contoh prediksi ke folder `reports/`.

### 6. Validasi Manual Mendekati Industri

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

## Struktur Proyek

```text
app/            demo Streamlit
assets/         aset visual demo
data/           raw, clean, annotated, silver, dan manual gold workflow
docs/           dokumentasi tambahan dan screenshot evidence
models/         output model lokal, tidak dikomit
notebooks/      eksplorasi dan eksperimen
reports/        metrik, laporan evaluasi, dan error analysis
resources/      lexicon atau resource pendukung
src/            skrip data, training, evaluasi, dan prediksi
tests/          unit test pipeline dan inference helper
```

## Verifikasi Lokal

```powershell
python -m unittest discover -s tests
python -m compileall src app tests
pip check
```

## Status Roadmap

- [x] Fase 0 - Inisialisasi proyek
- [x] Fase 1 - Pengumpulan dan pembersihan data
- [x] Fase 2 - Anotasi data format BIO
- [x] Fase 3 - Fine-tuning model
- [x] Fase 4 - Evaluasi
- [x] Fase 5 - Demo interaktif
- [x] Fase 6 - Dokumentasi dan finalisasi

## Catatan Batasan

Model ini adalah prototype riset/engineering untuk ekstraksi informasi teks
medis Bahasa Indonesia. Jangan gunakan sebagai alat diagnosis klinis. Untuk
klaim performa yang mendekati standar industri, evaluasi harus dijalankan ulang
hanya pada gold test set manual yang sudah melewati agreement antar annotator
dan conflict resolution.
