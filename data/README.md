# Data

This folder stores local data artifacts for the Medical NER Bahasa Indonesia
project.

## Phase 1 Source

The Phase 1 pipeline uses the public Hugging Face dataset
`iqbalpurba26/health-topic-dataset` as the primary source. It contains
Indonesian health forum questions and is suitable as a starting corpus for
medical NER annotation.

Generated data files:

- `data/raw/health_topic_dataset.jsonl`
- `data/clean/medical_text_corpus.txt`
- `data/clean/medical_text_corpus_metadata.csv`

The generated raw and clean data files are intentionally ignored by Git because
they are reproducible from `src/data_prep.py` and may contain public forum text.
