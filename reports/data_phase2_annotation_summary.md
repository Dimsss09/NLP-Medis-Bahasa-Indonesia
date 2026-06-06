# Phase 2 Annotation Summary

Generated at: 2026-06-06T17:21:30.400534+00:00

## Method

- Tokenized the clean corpus with a deterministic regex tokenizer.
- Applied longest-match lexicon annotation for GEJALA, OBAT, DIAGNOSIS, and ANATOMI.
- Applied regex/rule annotation for DOSIS patterns.
- Split records deterministically into train/val/test with seed 42.

## Caveat

This is a semi-automatic bootstrap dataset and should be manually reviewed before final model claims.

## Result

- Total records: 13052
- Total tokens: 104436

## Split Counts

| Split | Records | Tokens | GEJALA | OBAT | DOSIS | DIAGNOSIS | ANATOMI |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| train | 10441 | 83655 | 4389 | 551 | 341 | 473 | 3326 |
| val | 1305 | 10444 | 496 | 66 | 50 | 55 | 412 |
| test | 1306 | 10337 | 543 | 69 | 45 | 65 | 425 |
