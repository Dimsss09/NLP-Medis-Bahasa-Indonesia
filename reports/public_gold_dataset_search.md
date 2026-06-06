# Public Human-Annotated Dataset Search

## DetikHealth Medical NER Corpus

Source checked:

- JAIC article: `Medical Named Entity Recognition from Indonesian Health-News using BiLSTM-CRF with Static and Contextual Embeddings`
- DOI: `10.30871/jaic.v9i6.11574`

## Finding

The paper describes a relevant Indonesian medical NER corpus:

- Source domain: DetikHealth health-news articles.
- Size: 272 articles.
- Labels: Disease, Symptom, Drug.
- Annotation tool: Label Studio.
- Format: BIO.
- Annotators: two trained undergraduate annotators for a random 10% double-annotated subset.
- Agreement: Cohen's Kappa reported as 0.8-1.

However, the article page states that download data is not yet available. The
corpus is therefore useful as methodological evidence and a benchmark reference,
but it cannot currently be imported into this repository as public gold data.

## Recommendation

Keep two tracks separate:

1. Manual gold track:
   Use `data/manual_gold/annotator_1.conll` and
   `data/manual_gold/annotator_2.conll` for real human annotation,
   agreement, adjudication, and gold-test evaluation.

2. Silver annotation track:
   Use rules or LLM-assisted labels only as silver data for training expansion.
   Do not report silver labels as human gold or annotator agreement.

The best practical choice is a hybrid strategy: manual gold for evaluation,
silver labels for scaling training data.
