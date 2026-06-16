# Phase 9 Progress Summary

Generated at: 2026-06-16

## What Changed

- Applied final human adjudication decisions to `data/phase9_challenge_set/conflicts.tsv`.
- Generated Phase 9 gold file: `data/phase9_challenge_set/gold_resolved.conll`.
- Added Phase 9 adjudication policy notes in `data/phase9_challenge_set/adjudication_notes.md`.
- Added expanded-label silver training data in `data/phase9_expanded_silver/`.
- Trained expanded-label IndoBERT model:
  `models/indobert-medical-ner-id-phase9-expanded`.
- Updated evaluator so confusion matrices include labels found in gold/prediction,
  not only labels listed in the old config.

## Phase 9 Gold Set

- Sentences: 160
- Tokens: 1366
- Conflict rows resolved: 148
- Unresolved conflicts: 0

## Model Comparison

| Model | Evaluation set | Micro precision | Micro recall | Micro F1 |
| --- | --- | ---: | ---: | ---: |
| IndoBERT human-aligned | Phase 9 challenge | 0.6935 | 0.4080 | 0.5137 |
| IndoBERT phase9-expanded | Phase 9 challenge | 0.7422 | 0.6338 | 0.6837 |
| IndoBERT human-aligned | true gold 300 | 0.7967 | 0.6631 | 0.7238 |
| IndoBERT phase9-expanded | true gold 300 | 0.6304 | 0.6346 | 0.6325 |

## Expanded Model F1 per Entity on Phase 9

| Entity | F1 |
| --- | ---: |
| ALERGI | 0.9143 |
| ANATOMI | 0.8167 |
| DIAGNOSIS | 0.5862 |
| DOSIS | 0.0000 |
| GEJALA | 0.7029 |
| HASIL_LAB | 0.7917 |
| NILAI_LAB | 0.7692 |
| OBAT | 0.7429 |
| PROSEDUR | 0.5400 |
| RIWAYAT_PENYAKIT | 0.0000 |
| WAKTU_DURASI | 0.5345 |

## Interpretation

The expanded model is better for the new Phase 9 schema, especially `ALERGI`,
`HASIL_LAB`, and `NILAI_LAB`. However, it is weaker on the original true gold
benchmark than the previous human-aligned model.

This means the project has reached a real decision point:

1. Keep the 5-label human-aligned model as the main model for stable NER claims.
2. Promote the 11-label phase9-expanded model as the new direction, but collect
   more manual examples first.

## Next Human Decision Needed

Choose the project direction:

- Option A: keep the 5-label model as the default and treat Phase 9 as research.
- Option B: make the 11-label expanded schema the default and collect more human
  examples for weak labels.

Recommended: Option B only after adding manual examples for `RIWAYAT_PENYAKIT`,
`DOSIS`, `PROSEDUR`, and `WAKTU_DURASI`.
