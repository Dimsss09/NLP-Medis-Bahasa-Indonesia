# Adjudication Notes - Phase 9

Isi file ini saat menyelesaikan konflik annotator.

## Keputusan yang perlu dicatat

- Apakah `alergi` dipakai sebagai `ALERGI` atau tetap `DIAGNOSIS` pada konteks tertentu?
- Apakah `vaksin` dianggap `PROSEDUR` atau `OBAT`?
- Apakah kata waktu seperti `tahun` pada usia pasien tetap `WAKTU_DURASI` atau `O`?
- Apakah `kolesterol tinggi` menjadi `DIAGNOSIS`, atau `HASIL_LAB` + `NILAI_LAB`?

## Catatan keputusan final

- `alergi` -> `ALERGI`, bukan `DIAGNOSIS`. Dipakai `ALERGI` saat menyebut kondisi/reaksi/jenis alergi seperti `mengatasi alergi`, `obat alergi`, dan `alergi debu`. Hanya menjadi `I-RIWAYAT_PENYAKIT` bila menempel langsung pada kata `riwayat`, misalnya `riwayat alergi`.
- `vaksin`, `vaksinasi`, dan `divaksin` -> `PROSEDUR`, bukan `OBAT`. Nama target seperti `covid` atau `corona` mengikuti sebagai `I-PROSEDUR`.
- `tahun`, `bulan`, dan `minggu` pada usia tetap `WAKTU_DURASI` untuk sementara. Token satuan waktu belum dibedakan antara usia dan durasi demi konsistensi.
- `kolesterol tinggi` -> `kolesterol` sebagai `B-HASIL_LAB` dan `tinggi` sebagai `B-NILAI_LAB`, bukan `DIAGNOSIS`. Berlaku juga untuk `gula darah tinggi`, `asam urat`, `leukosit tinggi`, dan `trombosit rendah`.
- `wasir` -> `DIAGNOSIS`; yang menjadi `PROSEDUR` adalah `operasi`.
- `kuretase`, `pemeriksaan usg`, `vaksinasi`, `suntik`, dan tindakan sejenis -> `PROSEDUR`.
- `obat cacing` dan `nebulizer` -> `OBAT` sesuai pegangan alat/terapi/perawatan.
- `mabuk perjalanan` -> `GEJALA`, bukan `OBAT` atau `DIAGNOSIS`.
