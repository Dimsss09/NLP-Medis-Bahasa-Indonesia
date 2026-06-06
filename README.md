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

## Menjalankan Demo

```powershell
streamlit run app/demo.py
```

Untuk saat ini demo masih berupa shell awal. Inferensi akan diaktifkan setelah
fase training selesai.

## Status Roadmap

- [x] Fase 0 - Inisialisasi proyek
- [ ] Fase 1 - Pengumpulan dan pembersihan data
- [ ] Fase 2 - Anotasi data format BIO
- [ ] Fase 3 - Fine-tuning model
- [ ] Fase 4 - Evaluasi
- [ ] Fase 5 - Demo interaktif
- [ ] Fase 6 - Dokumentasi dan finalisasi
