# 3. Roadmap — Instruksi untuk AI (Kerjakan Sampai Selesai)

<aside>
🤖

Dokumen ini ditulis sebagai **instruksi (prompt) untuk AI agent** (mis. Cursor, Claude Code, atau asisten coding lain). Salin seluruh bagian "Instruksi utama" ke AI agent, lalu biarkan ia mengerjakan fase demi fase sampai semua kriteria selesai terpenuhi.

</aside>

## 📋 Instruksi utama untuk AI

```
KAMU ADALAH: ML/NLP engineer yang mengerjakan proyek Medical NER Bahasa Indonesia dari awal hingga selesai.

TUJUAN AKHIR: Menghasilkan repositori lengkap berisi model NER terlatih (berbasis IndoBERT) yang mengekstraksi entitas medis (GEJALA, OBAT, DOSIS, DIAGNOSIS, ANATOMI) dari teks Bahasa Indonesia, beserta evaluasi terukur, demo interaktif, dan dokumentasi.

ATURAN KERJA:
1. Kerjakan FASE demi FASE sesuai urutan di bawah. Jangan lompat fase.
2. Di akhir setiap fase, laporkan: apa yang dikerjakan, file yang dibuat, hasil/metrik, dan kendala.
3. Tulis kode yang bersih, modular, dan terkomentari. Sertakan docstring.
4. Setelah menyelesaikan satu fase, LANJUTKAN OTOMATIS ke fase berikutnya sampai SEMUA kriteria selesai terpenuhi. Jangan berhenti menunggu konfirmasi kecuali ada keputusan penting (mis. pilihan dataset) atau error yang butuh input manusia.
5. Jika sebuah dataset tidak dapat diakses, gunakan alternatif publik atau buat dataset contoh kecil, lalu catat asumsinya.
6. Selalu commit ke Git dengan pesan yang jelas di akhir setiap fase.

DEFINISI SELESAI (Definition of Done):
- Model terlatih tersimpan & dapat dimuat ulang.
- Laporan evaluasi (precision/recall/F1 per entitas) tersedia.
- Demo (Streamlit/Gradio) berjalan tanpa error.
- README.md lengkap & dapat diikuti orang lain.
- Semua kode ter-commit ke repositori.
```

## 🗺️ Fase pengerjaan

### Fase 0 — Inisialisasi proyek

- Buat struktur repo (lihat dokumen "Struktur Repo & Setup").
- Siapkan virtual environment + `requirements.txt`.
- Inisialisasi Git + `.gitignore`.
- **Selesai jika:** repo terstruktur & dependensi terpasang.

### Fase 1 — Pengumpulan & pembersihan data

- Kumpulkan teks medis Bahasa Indonesia (forum kesehatan publik / dataset terbuka).
- Bersihkan: hapus duplikat, normalisasi teks, pisah kalimat.
- Simpan ke `data/raw/` dan `data/clean/`.
- **Selesai jika:** ada korpus teks bersih siap anotasi.

### Fase 2 — Anotasi data (format BIO)

- Definisikan skema entitas (lihat dokumen "Skema Entitas & Panduan Anotasi").
- Anotasi dengan Label Studio/Doccano atau skrip semi-otomatis (lexicon obat/gejala) lalu koreksi manual.
- Ekspor ke format CoNLL/BIO; split train/val/test.
- **Selesai jika:** dataset BIO tersedia & terbagi.

### Fase 3 — Fine-tuning model

- Muat **IndoBERT** dari Hugging Face.
- Latih token classification (NER) pada data train.
- Simpan model & tokenizer ke `models/`.
- **Selesai jika:** model terlatih tersimpan.

### Fase 4 — Evaluasi

- Hitung precision/recall/F1 **per entitas** dengan `seqeval`.
- Buat confusion matrix & contoh prediksi benar/salah.
- Simpan laporan ke `reports/`.
- **Selesai jika:** laporan metrik lengkap tersedia.

### Fase 5 — Demo interaktif

- Bangun app Streamlit/Gradio: input teks → entitas tersorot berwarna.
- Pastikan berjalan lokal tanpa error.
- **Selesai jika:** demo dapat dijalankan & mengeluarkan hasil.

### Fase 6 — Dokumentasi & finalisasi

- Tulis `README.md`: deskripsi, cara instal, cara jalankan, hasil, screenshot demo.
- Sertakan badge/metrik & contoh penggunaan.
- (Opsional) Deploy ke Hugging Face Spaces.
- **Selesai jika:** README lengkap & semua ter-commit.

## 🗓️ Estimasi waktu (fleksibel)

| Fase | Estimasi |
| --- | --- |
| 0 — Inisialisasi | 0.5 hari |
| 1 — Data | 2–3 hari |
| 2 — Anotasi | 3–5 hari |
| 3 — Training | 1–2 hari |
| 4 — Evaluasi | 1 hari |
| 5 — Demo | 1–2 hari |
| 6 — Dokumentasi | 1 hari |

## ✅ Checklist penyelesaian global

- [ ]  Fase 0 — Inisialisasi proyek
- [ ]  Fase 1 — Data terkumpul & bersih
- [ ]  Fase 2 — Data teranotasi (BIO)
- [ ]  Fase 3 — Model terlatih
- [ ]  Fase 4 — Evaluasi terukur
- [ ]  Fase 5 — Demo berjalan
- [ ]  Fase 6 — Dokumentasi & publikasi