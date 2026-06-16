# Panduan Review Manual - 11 Label Boost

Pakai `docs/annotation_guidelines_11_label_journal_aligned.md` sebagai pegangan.

## Fokus Review

1. `RIWAYAT_PENYAKIT`
   - Tandai hanya bila jelas ada konteks riwayat.
   - Contoh: `riwayat TB`, `pernah menderita asma`.

2. `DOSIS`
   - Tandai angka+satuan, bentuk obat, frekuensi, dan aturan pakai.
   - Contoh: `500 mg`, `2 kali sehari`, `tablet`, `sirup`.

3. `PROSEDUR`
   - Tandai tindakan, pemeriksaan, vaksinasi, operasi, suntikan.
   - Contoh: `operasi caesar`, `pemeriksaan USG`, `vaksinasi covid`.

4. `WAKTU_DURASI`
   - Tandai ekspresi waktu/lama/frekuensi.
   - Contoh: `3 hari`, `2 minggu`, `pagi hari`, `tahun`.

## Jangan Lupa

- Jangan ubah token.
- Ubah label saja.
- Kalau draft salah, koreksi.
- Kalau ragu, catat di `human_review_status.tsv`.
