# Ekstraksi Informasi Otomatis dari Teks Medis Bahasa Indonesia

![Python](https://img.shields.io/badge/Python-3.12-blue)
![Model](https://img.shields.io/badge/Models-IndoBERT%20%2B%20XLM--R-teal)
![Demo](https://img.shields.io/badge/Demo-Streamlit-ff4b4b)
![Micro F1](https://img.shields.io/badge/Silver%20Micro%20F1-0.9996-brightgreen)
![Status](https://img.shields.io/badge/Phase%206-Finalized-success)

Proyek ini membangun sistem Named Entity Recognition (NER) untuk mengekstraksi
entitas medis dari teks Bahasa Indonesia. Entitas yang dikenali saat ini adalah
`GEJALA`, `OBAT`, `DOSIS`, `DIAGNOSIS`, dan `ANATOMI`.

Output utama proyek:

- pipeline data dari korpus mentah ke format BIO/CoNLL;
- dataset silver berbasis rules dan lexicon;
- fine-tuned IndoBERT sebagai model utama;
- fine-tuned XLM-RoBERTa sebagai model pembanding multibahasa;
- laporan evaluasi, perbandingan F1 per entitas, error analysis, dan model card;
- demo lokal Streamlit dengan highlight entitas berwarna.

## Hasil Singkat

Evaluasi engineering terbaru dijalankan pada test set semi-otomatis/silver (untuk melihat progres model tetapi belum sebagai klaim klinis final).

### 1. Named Entity Recognition (NER)

| Model | Role | Micro precision | Micro recall | Micro F1 |
| --- | --- | ---: | ---: | ---: |
| `indobert` | utama | 1.0000 | 0.9991 | 0.9996 |
| `xlm_roberta` | pembanding | 0.9656 | 0.9782 | 0.9718 |

Perbandingan F1 per entitas:

| Entity | IndoBERT F1 | XLM-R F1 |
| --- | ---: | ---: |
| ANATOMI | 1.0000 | 0.9744 |
| DIAGNOSIS | 1.0000 | 0.9924 |
| DOSIS | 0.9888 | 0.9462 |
| GEJALA | 1.0000 | 0.9688 |
| OBAT | 1.0000 | 0.9784 |

### 2. Assertion Status (Negation & Uncertainty)
*Model: Fine-tuned IndoBERT (`models/indobert-medical-assertion-id`)*
*Akurasi Keseluruhan: 99%*

| Kelas | Precision | Recall | F1-Score | Support |
| --- | ---: | ---: | ---: | ---: |
| `AFFIRMED` | 0.99 | 1.00 | 1.00 | 583 |
| `NEGATED` | 0.91 | 0.91 | 0.91 | 11 |
| `UNCERTAIN` | 1.00 | 0.79 | 0.88 | 14 |

### 3. Relation Extraction
*Model: Fine-tuned IndoBERT (`models/indobert-medical-relation-id`)*
*Akurasi Keseluruhan: 97%*

| Hubungan | Precision | Recall | F1-Score | Support |
| --- | ---: | ---: | ---: | ---: |
| `dosage_of` (`DOSIS` -> `OBAT`) | 0.88 | 1.00 | 0.93 | 7 |
| `located_in` (`GEJALA`/`DIAG` -> `ANATOMI`) | 0.98 | 0.99 | 0.99 | 267 |
| `treats` (`OBAT` -> `GEJALA`/`DIAG`) | 0.92 | 0.96 | 0.94 | 23 |
| `no_relation` (Tidak ada hubungan) | 0.82 | 0.67 | 0.74 | 21 |

Detail lengkap tersedia di folder `reports/`, termasuk `reports/model_comparison.md` dan `reports/relations_evaluation_report.md`.

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

Model hasil training disimpan secara lokal di `models/indobert-medical-ner-id`
dan `models/xlm-roberta-medical-ner-id`. Folder `models/` tidak dikomit karena
berisi file bobot besar.

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
2. Pilih model utama IndoBERT atau model pembanding XLM-R di sidebar.
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

Model utama yang digunakan adalah `indobenchmark/indobert-base-p1`, lalu
dibandingkan dengan model multibahasa `xlm-roberta-base`. Keduanya di-fine-tune
sebagai token classification model dengan data, split, dan hyperparameter yang
sama. Pipeline training membaca data BIO/CoNLL, menyelaraskan token label dengan
subword tokenizer masing-masing model, lalu menyimpan tokenizer, konfigurasi
label, dan bobot model ke folder `models/`.

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
  IndoBERT atau XLM-R token classification.
- CSS custom untuk background medical NLP, logo animasi, panel hasil, dan badge
  highlight entitas.
- Asset visual lokal di `assets/medical-ner-background.png`, di-embed sebagai
  data URI agar demo tetap berjalan tanpa server asset tambahan.

## Pipeline Proyek

### 1. Menyiapkan Data & NER (Tahap 1)

*   **Menyiapkan Data:**
    ```powershell
    python src/data_prep.py
    ```
    Mengambil dataset publik `iqbalpurba26/health-topic-dataset`, menyimpan salinan JSONL ke `data/raw/`, lalu membuat korpus bersih di `data/clean/medical_text_corpus.txt`.
*   **Membuat Anotasi BIO:**
    ```powershell
    python src/annotate_bio.py
    ```
    Membuat anotasi awal berbasis lexicon dan aturan dosis ke `data/annotated/train.conll`, `data/annotated/val.conll`, dan `data/annotated/test.conll`.
*   **Membuat Silver Dataset:**
    ```powershell
    python src/build_silver_dataset.py
    ```
    Membuat dataset `data/silver/` dari rules dan lexicon.
*   **Melatih Model NER:**
    ```powershell
    python src/train.py
    ```
    Melakukan fine-tuning semua model yang terdaftar di `config.yaml` (`indobert` dan `xlm_roberta`).
*   **Evaluasi Model NER:**
    ```powershell
    python src/evaluate.py
    ```
    Menghitung precision, recall, F1 dengan `seqeval` untuk kedua model NER.
*   **Validasi Manual Mendekati Industri:**
    ```powershell
    python src/prepare_manual_gold.py
    python src/annotation_agreement.py
    python src/resolve_gold.py
    python src/evaluate.py --test-file data/manual_gold/gold_resolved.conll --report-prefix gold
    python src/error_analysis.py
    ```

### 2. Hubungan Relasi & Negasi (Tahap 2)

*   **Membangun Dataset Relasi & Asersi:**
    ```powershell
    python src/build_relation_dataset.py
    ```
    Mengekstraksi entitas dari berkas CoNLL, mendeteksi penanda negasi/ketidakpastian untuk melabeli status asersi (`AFFIRMED`, `NEGATED`, `UNCERTAIN`), dan memasangkan kandidat entitas (mis. `DOSIS` terdekat ke `OBAT`) menggunakan aturan berbasis jarak untuk menghasilkan split data JSON di `data/relations/`.
*   **Melatih Model Assertion Status:**
    ```powershell
    python src/train_assertion.py
    ```
    Melatih classifier asersi 3-kelas menggunakan IndoBERT dengan menyematkan penanda `[START_ENT]` dan `[END_ENT]` di sekitar entitas target. Output disimpan di `models/indobert-medical-assertion-id`.
*   **Melatih Model Relation Extraction:**
    ```powershell
    python src/train_relation.py
    ```
    Melatih classifier hubungan 4-kelas (`dosage_of`, `treats`, `located_in`, `no_relation`) menggunakan IndoBERT dengan menyematkan penanda `[START_HEAD]`, `[END_HEAD]`, `[START_TAIL]`, dan `[END_TAIL]` di sekitar entitas yang dihubungkan. Output disimpan di `models/indobert-medical-relation-id`.
*   **Pipeline Evaluasi Relasi & Asersi:**
    ```powershell
    python src/evaluate_pipeline.py
    ```
    Menjalankan pengujian akhir terhadap model klasifikasi asersi dan relasi pada dataset uji serta menulis laporan metrik performa ke `reports/relations_evaluation_report.md`.

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

### 🟢 Tahap 1 — Fondasi NER
- [x] Fase 0 - Inisialisasi proyek
- [x] Fase 1 - Pengumpulan dan pembersihan data
- [x] Fase 2 - Anotasi data format BIO
- [x] Fase 3 - Fine-tuning model
- [x] Fase 4 - Evaluasi
- [x] Fase 5 - Demo interaktif
- [x] Fase 6 - Dokumentasi dan finalisasi

### 🔵 Tahap 2 — Relation & Negation Extraction
- [x] Skema data hubungan & negasi (`data/relations/`)
- [x] Skrip dataset generator (`src/build_relation_dataset.py`)
- [x] Model assertion (negasi/ragu) fine-tuned (`train_assertion.py`)
- [x] Model relation extraction fine-tuned (`train_relation.py`)
- [x] Integrated prediction pipeline (`src/predict_pipeline.py`)
- [x] Evaluasi performa pipeline (`src/evaluate_pipeline.py`)
- [x] Integrasi UI demo interaktif dengan visualisasi relasi & negasi

### 🟣 Tahap 3 — Medical Knowledge Graph (Selanjutnya)
- [ ] Rancang skema database graph (Nodes: Disease, Symptom, Drug, etc.)
- [ ] Normalisasi entitas medis ke konsep standar
- [ ] Export data ke format Graph (RDF/NetworkX/Neo4j)
- [ ] Visualisasi graph interaktif di web demo Streamlit

## Catatan Batasan

Model ini adalah prototype riset/engineering untuk ekstraksi informasi teks
medis Bahasa Indonesia. Jangan gunakan sebagai alat diagnosis klinis. Untuk
klaim performa yang mendekati standar industri, evaluasi harus dijalankan ulang
hanya pada gold test set manual yang sudah melewati agreement antar annotator
dan conflict resolution.
