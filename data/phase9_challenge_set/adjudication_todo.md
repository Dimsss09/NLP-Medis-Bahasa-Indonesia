# Phase 9 Adjudication TODO

Agreement sudah dihitung. Ada 148 konflik token.

Status terbaru: 15 konflik manual sudah diputuskan oleh manusia dan diterapkan
ke `conflicts_suggested.tsv` serta `conflicts.tsv`.

## Cara pakai

1. `conflicts.tsv` sudah berisi label final.
2. Jalankan `src/resolve_gold.py`.
3. Pakai `gold_resolved.conll` sebagai challenge gold internal Fase 9.

## Konflik yang perlu keputusan manual

| Sentence | Token | Annotator 1 | Annotator 2 | Teks |
| ---: | --- | --- | --- | --- |
| 28 | wasir | `B-DIAGNOSIS` | `I-PROSEDUR` | resep obat yang digunakan pasca operasi wasir |
| 34 | pemeriksaan | `B-PROSEDUR` | `I-RIWAYAT_PENYAKIT` | haid yang tidak teratur dengan riwayat pemeriksaan usg yang normal |
| 34 | usg | `I-PROSEDUR` | `I-RIWAYAT_PENYAKIT` | haid yang tidak teratur dengan riwayat pemeriksaan usg yang normal |
| 44 | keloid | `B-DIAGNOSIS` | `I-PROSEDUR` | mengatasi haid berkepanjangan setelah suntik keloid dengan menggunakan obat kortikosteroid |
| 45 | kuretase | `B-PROSEDUR` | `I-RIWAYAT_PENYAKIT` | haid tidak teratur dan keluar asi sedikit dengan riwayat kuretase bulan lalu |
| 52 | alergi | `B-ALERGI` | `I-RIWAYAT_PENYAKIT` | obat untuk mengatasi rasa nyeri pada riwayat penderita alergi |
| 60 | kulit | `B-ANATOMI` | `I-RIWAYAT_PENYAKIT` | ada riwayat kulit bentolbentol usai divaksin apakah sekarang masih boleh vaksinasi covid |
| 60 | bentolbentol | `B-GEJALA` | `I-RIWAYAT_PENYAKIT` | ada riwayat kulit bentolbentol usai divaksin apakah sekarang masih boleh vaksinasi covid |
| 62 | paruparu | `I-RIWAYAT_PENYAKIT` | `B-DIAGNOSIS` | pemberian obat antiparasit pada pasien covid dengan riwayat penyakit diabetes dan paruparu |
| 78 | cacing | `I-OBAT` | `B-DIAGNOSIS` | aturan konsumsi obat cacing dibulan puasa |
| 81 | mabuk | `I-OBAT` | `B-DIAGNOSIS` | kapan boleh minum obat mabuk perjalanan setelah minum obat herbal |
| 81 | perjalanan | `I-OBAT` | `I-DIAGNOSIS` | kapan boleh minum obat mabuk perjalanan setelah minum obat herbal |
| 136 | nebulizer | `I-OBAT` | `B-PROSEDUR` | obat nebulizer untuk anak tahun |
| 137 | cacing | `I-OBAT` | `B-DIAGNOSIS` | anak usia tahun mengeluh nyeri perut bawah setelah minum obat cacing |
| 159 | alergi | `B-ALERGI` | `I-OBAT` | gatal yang kembali muncul setelah konsumsi obat anti alergi |

## Pegangan keputusan

- Kalau kata adalah nama penyakit/kondisi, pakai `DIAGNOSIS`.
- Kalau kata adalah tindakan/pemeriksaan, pakai `PROSEDUR`.
- Kalau kata adalah bagian dari frasa riwayat penyakit, pakai `RIWAYAT_PENYAKIT`.
- Kalau kata adalah alat/terapi/perawatan, pakai `OBAT`.
- Kalau kata adalah keluhan, pakai `GEJALA`.
- Kalau kata adalah jenis alergi atau kondisi alergi, pakai `ALERGI`.
