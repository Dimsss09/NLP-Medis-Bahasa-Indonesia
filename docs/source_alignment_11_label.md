# Source Alignment for 11-Label Medical NER

This document records why the expanded schema is reasonable compared with
clinical NLP and pharmacovigilance literature.

## Sources Consulted

1. i2b2/VA 2010 Concept Annotation Guidelines
   - Used to map `DIAGNOSIS`/`GEJALA` to medical problems.
   - Used to map `PROSEDUR` to treatments and interventions.
   - Used to map `HASIL_LAB` to tests/lab/diagnostic procedures.

2. n2c2 2018 ADE and Medication Extraction
   - Used to justify medication attributes such as dosage, duration, route,
     frequency, and reason.
   - Used to justify keeping `DOSIS` and `WAKTU_DURASI` as explicit entities
     around medication/therapy context.

3. CADEC
   - Used to justify drug safety oriented labels such as drug, symptom/adverse
     effect, disease, and allergy-like reaction mentions.
   - Used to justify multi-stage annotation, inter-annotator agreement, and
     final review/adjudication.

## Mapping to This Project

| Literature concept | Project label |
| --- | --- |
| Medical problem, sign, symptom | `DIAGNOSIS`, `GEJALA`, `ALERGI` |
| Treatment/procedure/intervention | `PROSEDUR`, sometimes `OBAT` |
| Test/lab/diagnostic procedure | `PROSEDUR`, `HASIL_LAB`, `NILAI_LAB` |
| Drug/medication | `OBAT` |
| Dosage/strength/form/frequency | `DOSIS` |
| Duration/date/relative date | `WAKTU_DURASI` |
| Past/current history marker | `RIWAYAT_PENYAKIT` |

## Local Policy Choices

- `ALERGI` is split from generic `DIAGNOSIS` because the project needs
  allergy-specific extraction for medication safety.
- `HASIL_LAB` and `NILAI_LAB` are split so `kolesterol tinggi` can be modeled
  as parameter plus value/status.
- `RIWAYAT_PENYAKIT` is intentionally strict: only explicit history contexts
  are labeled.
- `WAKTU_DURASI` is broad for now and includes age units. This can be split in a
  later schema if age becomes important.
