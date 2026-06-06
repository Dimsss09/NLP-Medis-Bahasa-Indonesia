# 2. Skema Entitas & Panduan Anotasi

<aside>
🏷️

Panduan untuk mendefinisikan entitas dan menganotasi data secara konsisten. Konsistensi anotasi = kualitas model.

</aside>

## Format anotasi: BIO

Setiap token diberi label dengan skema **BIO**:

- `B-<ENTITAS>` — token **awal** (Begin) sebuah entitas.
- `I-<ENTITAS>` — token **lanjutan** (Inside) dari entitas yang sama.
- `O` — token di **luar** (Outside) entitas apa pun.

### Contoh

| Token | Label |
| --- | --- |
| Pasien | O |
| mengalami | O |
| demam | B-GEJALA |
| tinggi | I-GEJALA |
| dan | O |
| diberi | O |
| paracetamol | B-OBAT |
| 500 | B-DOSIS |
| mg | I-DOSIS |

## Definisi entitas (rinci)

### `GEJALA`

Keluhan subjektif/objektif yang dirasakan pasien.

- ✅ Termasuk: "demam", "sesak napas", "nyeri ulu hati".
- ❌ Bukan: nama penyakit (itu `DIAGNOSIS`).

### `OBAT`

Nama zat/produk obat.

- ✅ Termasuk: nama generik & merek dagang.
- ❌ Bukan: bentuk sediaan umum tanpa nama ("tablet" saja).

### `DOSIS`

Takaran, frekuensi, atau aturan pakai.

- ✅ Termasuk: "500 mg", "2x sehari", "sesudah makan".

### `DIAGNOSIS`

Nama penyakit/kondisi medis.

- ✅ Termasuk: "demam berdarah", "diabetes melitus".

### `ANATOMI`

Bagian tubuh atau organ.

- ✅ Termasuk: "jantung", "lambung", "lengan kiri".

## Aturan anotasi penting

1. **Anotasi rentang terpanjang yang bermakna** (mis. "nyeri dada sebelah kiri" sebagai satu `GEJALA`).
2. **Konsisten** untuk kasus ambigu — catat keputusan di "Catatan kasus ambigu" di bawah.
3. Jika ragu antara dua label, prioritaskan konteks klinis.
4. Jangan anotasi kata sambung/keterangan yang tidak relevan.

## Alat anotasi yang disarankan

- **Label Studio** (UI ramah, ekspor ke CoNLL/JSON).
- **Doccano** (ringan, khusus NLP labeling).

## Catatan kasus ambigu

> Gunakan toggle ini untuk mencatat keputusan anotasi pada kasus yang membingungkan, agar konsisten antar anotator.
> 
- Daftar keputusan kasus ambigu
    - Contoh: "darah tinggi" → dianotasi sebagai `DIAGNOSIS` (sinonim hipertensi), bukan `GEJALA`.