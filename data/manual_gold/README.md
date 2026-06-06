# Manual Gold Test Annotation Instructions

Generated at: 2026-06-06T18:26:00.293571+00:00

## Purpose

This package contains 400 sampled Indonesian medical texts for manual
NER annotation. Use it to create an industry-leaning gold test set.

## Files

- `sample_texts.tsv`: source texts selected for manual annotation.
- `annotator_1.conll`: file for annotator 1.
- `annotator_2.conll`: file for annotator 2.
- `gold_resolved.conll`: created later by `src/resolve_gold.py`.

## Labels

Allowed BIO labels:

- `O`
- `B-GEJALA`
- `I-GEJALA`
- `B-OBAT`
- `I-OBAT`
- `B-DOSIS`
- `I-DOSIS`
- `B-DIAGNOSIS`
- `I-DIAGNOSIS`
- `B-ANATOMI`
- `I-ANATOMI`

## Rules

- Annotate independently. Annotator 1 and annotator 2 should not inspect each other's work.
- Use the longest meaningful clinical span.
- Keep BIO valid: each entity starts with `B-...`; continuation tokens use `I-...`.
- Use `O` for tokens outside any target entity.
- Keep tokens unchanged. Edit only the label column.
- If uncertain, choose the most clinically relevant label and record the case in review notes.

## Workflow

1. Annotator 1 edits `annotator_1.conll`.
2. Annotator 2 edits `annotator_2.conll`.
3. Run `python src/annotation_agreement.py`.
4. Resolve disagreements in `data/manual_gold/conflicts.tsv`.
5. Run `python src/resolve_gold.py` to create `gold_resolved.conll`.
6. Evaluate with `python src/evaluate.py --test-file data/manual_gold/gold_resolved.conll --report-prefix gold`.
