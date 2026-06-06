# Phase 1 Data Summary

Generated at: 2026-06-06T17:10:34.235115+00:00

## Source

- Primary dataset: iqbalpurba26/health-topic-dataset
- Output corpus: data/clean/medical_text_corpus.txt
- Metadata: data/clean/medical_text_corpus_metadata.csv

## Cleaning

- Normalized whitespace.
- Removed empty texts.
- Removed exact duplicate texts case-insensitively.
- Preserved original casing because clinical terms and medicine names can carry useful cues.

## Result

- Clean records: 13052
- Average whitespace-token count: 8.00

## Records by source

- iqbalpurba26/health-topic-dataset: 13052

## Next Phase

Use `data/clean/medical_text_corpus.txt` as the input corpus for BIO annotation.
