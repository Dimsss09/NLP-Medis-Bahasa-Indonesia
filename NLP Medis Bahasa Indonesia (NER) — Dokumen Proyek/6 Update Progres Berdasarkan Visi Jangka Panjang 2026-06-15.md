# Update Progres Berdasarkan Visi Jangka Panjang - 2026-06-15

Dokumen ini merangkum posisi terbaru proyek setelah true human gold selesai dibuat dan model IndoBERT dilatih ulang mengikuti aturan adjudikasi manusia.

## Posisi proyek sekarang

Proyek sudah tidak lagi hanya berupa demo NER berbasis silver dataset. Sekarang proyek punya benchmark manusia kecil yang bisa dipakai sebagai ukuran lebih jujur.

Yang sudah selesai:

- 300 teks untuk true human gold.
- 2 annotator manusia.
- Conflict resolution manual.
- Catatan adjudication.
- Evaluasi baseline IndoBERT dan XLM-R.
- Training ulang IndoBERT dengan data tambahan yang mengikuti aturan adjudikasi.
- Evaluasi ulang model human-aligned ke true gold.

## Hasil model terbaru

| Model | Data evaluasi | Micro F1 |
| --- | --- | --- |
| IndoBERT baseline | true human gold 300 | 0.3649 |
| XLM-R baseline | true human gold 300 | 0.3481 |
| IndoBERT human-aligned | true human gold 300 | 0.7238 |

Makna sederhananya: setelah aturan manusia dipakai untuk membuat data training tambahan, model jauh lebih cocok dengan data true gold.

## Status berdasarkan visi jangka panjang

| Tahap | Target visi | Status |
| --- | --- | --- |
| Tahap 1 | Fondasi NER | Selesai dan sudah diperkuat dengan true gold. |
| Tahap 2 | Relasi dan negasi | Prototype ada, tetapi evaluasi manualnya perlu ditambah. |
| Tahap 3 | Knowledge Graph | Prototype ada, tetapi masih cocok untuk demo, belum skala besar. |
| Tahap 4 | QA klinis/RAG | Prototype ada, tetapi retrieval dan rujukan sumber perlu diperkuat. |
| Tahap 5 | Benchmark publik | Belum publik. Baru aman disebut benchmark internal. |

## Kekurangan utama yang masih tersisa

1. True gold masih kecil.
2. Label `DOSIS`, `OBAT`, dan `GEJALA` masih perlu contoh tambahan.
3. Label medis penting seperti prosedur, alergi, hasil lab, nilai lab, waktu/durasi, dan riwayat penyakit belum masuk skema utama.
4. RAG masih perlu semantic retrieval.
5. Knowledge Graph masih berbasis file/memori, belum graph database.
6. Aplikasi masih dominan Streamlit, belum dipisah menjadi API backend.

## Yang sebaiknya dilakukan sekarang

Urutan paling masuk akal:

1. Tambah 100 sampai 200 contoh manual khusus untuk label yang masih lemah.
2. Buat challenge set kecil berisi kasus sulit, misalnya alergi, prosedur, hasil lab, durasi, negasi, dan riwayat penyakit.
3. Perluas label secara bertahap, jangan semuanya sekaligus.
4. Latih ulang model setelah data tambahan siap.
5. Evaluasi ulang ke true gold dan challenge set.
6. Setelah model stabil, buat API FastAPI.
7. Setelah API siap, upgrade RAG ke vector retrieval.
8. Setelah itu baru pikirkan rilis publik atau Hugging Face.

## Prinsip penting

Jangan mencampur data evaluasi true gold ke training. True gold harus tetap menjadi alat ukur, bukan bahan latihan model.

Jangan klaim performa klinis. Klaim yang aman saat ini adalah: proyek memiliki benchmark internal berbasis anotasi manusia dan model human-aligned menunjukkan peningkatan besar dibanding baseline.
