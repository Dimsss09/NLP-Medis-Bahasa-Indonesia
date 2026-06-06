# 1. Ringkasan & README Proyek

<aside>
🎯

Dokumen ringkasan proyek — jadikan ini dasar untuk file `README.md` di GitHub.

</aside>

## Judul proyek

**Ekstraksi Informasi Otomatis dari Teks Medis Bahasa Indonesia (Medical NER)**

## Latar belakang

Mayoritas riset & model NER medis berbahasa Inggris. Model berbahasa Inggris berkinerja buruk pada teks medis Bahasa Indonesia. Proyek ini membangun model **Named Entity Recognition (NER)** yang mengekstraksi entitas medis penting dari teks Bahasa Indonesia — mengisi celah yang jarang digarap.

## Tujuan

- Membangun model NER yang dapat mengenali entitas medis (gejala, obat, dosis, diagnosis, anatomi) pada teks Bahasa Indonesia.
- Mencapai skor F1 yang baik per entitas dan mendokumentasikannya secara terukur.
- Menyediakan demo interaktif yang dapat dicoba siapa pun.

## Ruang lingkup

- ✅ **Termasuk:** pengumpulan data, anotasi, fine-tuning IndoBERT, evaluasi, demo.
- ❌ **Tidak termasuk:** triase end-to-end, chatbot, integrasi rumah sakit nyata (bisa jadi pengembangan lanjutan).

## Entitas yang diekstraksi

| Label | Deskripsi | Contoh |
| --- | --- | --- |
| `GEJALA` | Keluhan/gejala pasien | demam, batuk, nyeri dada |
| `OBAT` | Nama obat | paracetamol, amoxicillin |
| `DOSIS` | Takaran/dosis obat | 500 mg, 2x sehari |
| `DIAGNOSIS` | Penyakit/diagnosis | demam berdarah, hipertensi |
| `ANATOMI` | Bagian tubuh | kepala, lambung, paru |

## Tech stack

- **Bahasa:** Python
- **Model:** IndoBERT (Hugging Face Transformers)
- **Anotasi:** Label Studio / Doccano (format BIO)
- **Evaluasi:** `seqeval` (precision, recall, F1 per entitas)
- **Demo:** Streamlit / Gradio
- **Lainnya:** pandas, scikit-learn, PyTorch

## Deliverables

- [ ]  Dataset teranotasi (format BIO)
- [ ]  Notebook/skrip training & evaluasi
- [ ]  Model terlatih + laporan metrik
- [ ]  Aplikasi demo
- [ ]  README + dokumentasi lengkap di GitHub

## Hasil (diisi setelah selesai)

> Contoh: *"Model mencapai F1 0.87 (micro-average) pada test set, dengan performa tertinggi pada entitas OBAT (F1 0.92)."*
>