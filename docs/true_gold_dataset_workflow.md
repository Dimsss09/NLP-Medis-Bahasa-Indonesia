# Panduan Memberi Label Data Teks Medis

Dokumen ini dibuat untuk membantu kamu dan temanmu membuat data evaluasi yang
lebih terpercaya untuk proyek Medical NER Bahasa Indonesia.

Bahasa sederhananya: kita ingin meminta 2 orang membaca teks medis pendek, lalu
menandai kata-kata penting seperti gejala, obat, dosis, penyakit, dan bagian
tubuh.

Target awal: 300 teks dulu. Jangan langsung 500 supaya pekerjaannya tidak terlalu
berat.

## 1. Tujuan Pekerjaan Ini

Saat ini proyek sudah punya label otomatis dari program. Label otomatis itu
bagus untuk latihan awal model, tetapi belum cukup kuat untuk dijadikan bukti
bahwa model benar-benar bagus.

Karena itu kita perlu data yang diberi label oleh manusia.

Alurnya:

1. Dua orang memberi label secara terpisah.
2. Hasil dua orang dibandingkan.
3. Kalau ada perbedaan, kita bahas dan pilih label final.
4. Hasil final dipakai untuk menguji model.

## 2. Siapa yang Bisa Membantu Memberi Label

Tidak harus dokter.

Yang penting orangnya mau membaca panduan ini dan memberi label dengan teliti.

Bisa:

- kamu dan satu teman;
- dua teman;
- mahasiswa kesehatan, farmasi, keperawatan, atau kedokteran;
- mahasiswa non-kesehatan juga boleh, asal diberi contoh yang jelas.

Kalau ada dokter atau orang kesehatan, bagus. Tapi mereka tidak wajib memberi
label semua data. Mereka bisa diminta membantu hanya saat ada kasus yang
membingungkan.

## 3. Hal yang Tidak Boleh Dilakukan

Penting:

- Jangan melihat hasil label teman sebelum pekerjaan selesai.
- Jangan berdiskusi tentang jawaban tiap kalimat sebelum hasil dibandingkan.
- Jangan mengubah kata-kata di file.
- Jangan menghapus baris.
- Jangan menambah kata baru.
- Tugas annotator hanya mengganti label di sebelah kanan kata.

Contoh:

```text
demam O
```

boleh diubah menjadi:

```text
demam B-GEJALA
```

Tapi jangan mengubah kata `demam` menjadi kata lain.

## 4. Label yang Dipakai

Untuk tahap pertama, kita hanya pakai 5 jenis label.

| Label | Arti Sederhana | Contoh |
| --- | --- | --- |
| `GEJALA` | keluhan yang dirasakan pasien | demam, batuk, nyeri, gatal |
| `OBAT` | nama obat atau jenis obat | paracetamol, amoxicillin, insulin |
| `DOSIS` | jumlah obat atau aturan minum obat | 500 mg, 3x sehari, selama 5 hari |
| `DIAGNOSIS` | nama penyakit atau kondisi medis | diabetes, asma, hipertensi |
| `ANATOMI` | bagian tubuh | kepala, dada, tangan, kulit |

Untuk sekarang, jangan dulu menambah label lain seperti hasil lab atau prosedur.
Itu bisa dikerjakan di tahap berikutnya.

## 5. Cara Memberi Label

Di file, setiap kata punya label di sebelah kanannya.

Contoh awal:

```text
Pasien O
mengalami O
demam O
tinggi O
```

Kalau `demam tinggi` adalah gejala, ubah menjadi:

```text
Pasien O
mengalami O
demam B-GEJALA
tinggi I-GEJALA
```

## 6. Arti O, B, dan I

Ada 3 bentuk label:

| Bentuk | Artinya |
| --- | --- |
| `O` | kata biasa, bukan bagian penting medis |
| `B-...` | kata pertama dari bagian penting medis |
| `I-...` | kata lanjutan dari bagian penting medis yang sama |

Cara mudah mengingat:

- Kalau hanya 1 kata penting, pakai `B-`.
- Kalau ada 2 kata atau lebih, kata pertama pakai `B-`, kata berikutnya pakai
  `I-`.

Contoh 1 kata:

```text
batuk B-GEJALA
```

Contoh 2 kata:

```text
demam B-GEJALA
tinggi I-GEJALA
```

Contoh 3 kata:

```text
nyeri B-GEJALA
dada I-GEJALA
kiri I-GEJALA
```

## 7. Contoh Label Lengkap

Contoh kalimat:

```text
Pasien minum paracetamol 500 mg
```

Labelnya:

```text
Pasien O
minum O
paracetamol B-OBAT
500 B-DOSIS
mg I-DOSIS
```

Penjelasan:

- `Pasien` bukan gejala, obat, dosis, penyakit, atau bagian tubuh, jadi `O`.
- `minum` juga kata biasa, jadi `O`.
- `paracetamol` adalah obat, jadi `B-OBAT`.
- `500 mg` adalah dosis. `500` kata pertama, jadi `B-DOSIS`. `mg` lanjutannya,
  jadi `I-DOSIS`.

Contoh lain:

```text
Pasien diabetes dan nyeri pada kaki
```

Labelnya:

```text
Pasien O
diabetes B-DIAGNOSIS
dan O
nyeri B-GEJALA
pada O
kaki B-ANATOMI
```

## 8. Panduan untuk Kasus yang Sering Membingungkan

Gunakan aturan sederhana ini.

| Teks | Label yang Dipakai |
| --- | --- |
| `demam tinggi` | `demam B-GEJALA`, `tinggi I-GEJALA` |
| `batuk kering` | `batuk B-GEJALA`, `kering I-GEJALA` |
| `nyeri dada` | biasanya dianggap `GEJALA` |
| `dada` saja | `ANATOMI` |
| `sakit kepala` | `GEJALA` |
| `kepala` saja | `ANATOMI` |
| `500 mg` | `DOSIS` |
| `3x sehari` | `DOSIS` |
| `selama 5 hari` kalau membahas aturan obat | `DOSIS` |
| `diabetes melitus` | `DIAGNOSIS` |
| `obat batuk` kalau maksudnya jenis obat | `OBAT` |

Kalau masih ragu, tetap pilih label yang menurutmu paling masuk akal. Nanti
perbedaan jawaban akan dicek pada tahap penyelesaian konflik.

## 9. File yang Akan Dikerjakan

Kita akan membuat 2 file untuk 2 orang.

Annotator 1 mengerjakan:

```text
data/manual_gold/annotator_1.conll
```

Annotator 2 mengerjakan:

```text
data/manual_gold/annotator_2.conll
```

Masing-masing orang hanya mengedit file miliknya.

## 10. Cara Menyiapkan File

Bagian ini bisa dikerjakan oleh pemilik proyek, bukan oleh teman annotator.

Jalankan perintah ini dari folder proyek:

```powershell
.\venv\Scripts\python.exe src\prepare_manual_gold.py --sample-size 300
```

Perintah itu akan membuat file untuk annotator.

Jangan memakai script simulasi untuk membuat label gold. Label harus benar-benar
dikerjakan manusia.

## 11. Cara Kerja untuk Annotator

Untuk teman yang membantu memberi label:

1. Buka file yang diberikan.
2. Baca teks per kalimat.
3. Lihat tiap kata.
4. Jika kata itu bukan bagian medis penting, biarkan `O`.
5. Jika kata itu gejala, obat, dosis, diagnosis, atau bagian tubuh, ubah labelnya.
6. Jangan mengubah kata, tanda baca, atau urutan baris.
7. Kerjakan sendiri dulu sampai selesai.

Contoh sebelum:

```text
Pasien O
mengalami O
demam O
tinggi O
dan O
batuk O
```

Contoh sesudah:

```text
Pasien O
mengalami O
demam B-GEJALA
tinggi I-GEJALA
dan O
batuk B-GEJALA
```

## 12. Setelah Dua Orang Selesai

Bagian ini dikerjakan oleh pemilik proyek.

Jalankan:

```powershell
.\venv\Scripts\python.exe src\annotation_agreement.py
```

Hasilnya akan menunjukkan:

- seberapa sering dua annotator setuju;
- berapa banyak perbedaan label;
- daftar kata yang labelnya berbeda.

File konflik akan muncul di:

```text
data/manual_gold/conflicts.tsv
```

## 13. Menyelesaikan Perbedaan Jawaban

Kalau annotator 1 dan annotator 2 berbeda pendapat, kita harus memilih label
final secara manual.

Buka:

```text
data/manual_gold/conflicts.tsv
```

Di sana ada kolom `resolved_label`.

Isi kolom itu dengan label final.

Contoh:

```text
token: dada
annotator 1: B-ANATOMI
annotator 2: I-GEJALA
label final: B-ANATOMI
```

Cara memilih label final:

1. Baca kalimat aslinya.
2. Lihat konteks kata tersebut.
3. Cocokkan dengan panduan label.
4. Pilih label yang paling tepat.
5. Kalau bingung, tulis catatan dan tanyakan ke orang yang lebih paham medis jika
   ada.

## 14. Catatan Penyelesaian Konflik

Selain mengisi label final, buat catatan singkat supaya prosesnya jelas.

Buat file:

```text
data/manual_gold/adjudication_notes.md
```

Isi dengan format sederhana seperti ini:

```markdown
# Catatan Penyelesaian Konflik

Tanggal:
Nama penyelesai konflik:
Annotator 1:
Annotator 2:
Jumlah teks:
Jumlah konflik:

## Aturan yang Dipakai

- Konflik diselesaikan dengan membaca kalimat lengkap.
- Kata tidak diubah, hanya labelnya yang dipilih.
- Jika frasa menunjukkan keluhan pasien, dipilih GEJALA.
- Jika kata adalah bagian tubuh, dipilih ANATOMI.
- Jika kata menunjukkan jumlah atau aturan minum obat, dipilih DOSIS.

## Contoh Konflik Penting

1. Kalimat nomor:
   Kata:
   Label annotator 1:
   Label annotator 2:
   Label final:
   Alasan:

2. Kalimat nomor:
   Kata:
   Label annotator 1:
   Label annotator 2:
   Label final:
   Alasan:

## Catatan Keterbatasan

- Annotator bukan dokter spesialis.
- Data ini dipakai untuk menguji prototype model, bukan untuk keputusan klinis.
- Kasus yang sangat ambigu sebaiknya dicek lagi oleh orang medis.
```

## 15. Membuat File Gold Final

Setelah semua konflik sudah diberi label final, jalankan:

```powershell
.\venv\Scripts\python.exe src\resolve_gold.py
```

Output akhirnya:

```text
data/manual_gold/gold_resolved.conll
```

File inilah yang disebut gold dataset final.

## 16. Menguji Model dengan Data Gold

Setelah file gold final jadi, jalankan:

```powershell
.\venv\Scripts\python.exe src\evaluate.py --test-file data/manual_gold/gold_resolved.conll --report-prefix true_gold
```

Hasil evaluasi akan tersimpan di folder:

```text
reports/
```

## 17. Kalimat yang Aman untuk Laporan

Kalimat yang aman:

```text
Model dievaluasi pada 300 teks yang diberi label oleh dua annotator manusia
secara independen. Perbedaan label diselesaikan melalui pengecekan manual dan
dicatat dalam catatan adjudication.
```

Kalau annotator bukan dokter, jangan menulis:

```text
Model sudah tervalidasi klinis.
```

Lebih aman menulis:

```text
Dataset ini digunakan untuk evaluasi prototype dan belum menjadi validasi klinis
formal.
```

## 18. Checklist Kerja

Ikuti urutan ini:

- [ ] Pilih satu teman untuk menjadi annotator kedua.
- [ ] Jelaskan isi dokumen ini ke temanmu.
- [ ] Buat 300 teks anotasi dengan script persiapan.
- [ ] Kamu isi file `annotator_1.conll`.
- [ ] Temanmu isi file `annotator_2.conll`.
- [ ] Jangan saling melihat hasil sebelum selesai.
- [ ] Hitung hasil perbandingan dua annotator.
- [ ] Buka daftar konflik.
- [ ] Isi label final untuk konflik secara manual.
- [ ] Buat catatan penyelesaian konflik.
- [ ] Buat file gold final.
- [ ] Evaluasi model memakai file gold final.

## 19. Tahap Berikutnya

Setelah tahap ini selesai, baru boleh memikirkan label tambahan seperti:

- prosedur medis;
- hasil lab;
- nilai lab;
- waktu atau durasi;
- alergi;
- riwayat penyakit.

Label tambahan juga perlu diberi label oleh annotator. Jadi jangan dimasukkan
dulu kalau temanmu belum siap, karena bisa membuat pekerjaan menjadi terlalu
rumit.
