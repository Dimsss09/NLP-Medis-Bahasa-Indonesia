# Model Card: Indonesian Medical NER Bootstrap

## Model Details

- Base model: `indobenchmark/indobert-base-p1`
- Task: token classification / named entity recognition
- Labels: `GEJALA`, `OBAT`, `DOSIS`, `DIAGNOSIS`, `ANATOMI`
- Current model path: `models/indobert-medical-ner-id`

## Intended Use

This model is intended for research and portfolio demonstration of Indonesian
medical NER. It can help identify candidate spans for symptoms, medicines,
dosages, diagnoses, and anatomy mentions in short Indonesian health texts.

## Out-of-Scope Use

Do not use this model for clinical decision making, diagnosis, treatment
recommendations, patient triage, or medication safety checks.

## Training Data

The current training data is derived from a public Indonesian health-topic
dataset and bootstrapped with semi-automatic BIO labels. The labels have not yet
been fully validated by independent human annotators.

## Evaluation

The current Phase 4 evaluation is an engineering benchmark against
semi-automatic labels. It is not an industry-grade or clinical validation.

Current larger-bootstrap test metrics against semi-automatic labels:

- Micro precision: 0.9556
- Micro recall: 0.9765
- Micro F1: 0.9659
- Token accuracy: 0.9931

## Limitations

- The gold labels are not yet manually adjudicated.
- `DOSIS` recall is currently poor.
- `OBAT` recall is currently low.
- Performance on long clinical notes, abbreviations, typos, and real hospital
  records is unknown.

## Recommended Validation Before Use

- Double annotate a 300-500 sentence held-out test set.
- Measure inter-annotator agreement.
- Resolve conflicts into a gold test set.
- Evaluate the model only against that gold set for any public claims.
- Add a domain expert review for medical safety-sensitive labels.

## Public Dataset Search Note

A relevant DetikHealth medical NER corpus is described in the JAIC paper
`Medical Named Entity Recognition from Indonesian Health-News using BiLSTM-CRF
with Static and Contextual Embeddings`, but the article page indicates that the
download data is not yet available. This project therefore keeps a local manual
gold workflow and treats any rules or LLM-generated expansion as silver labels.
