"""Evaluate the trained Indonesian medical NER model."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

import torch
import yaml
import numpy as np
from seqeval.metrics import classification_report, f1_score, precision_score, recall_score
from sklearn.metrics import confusion_matrix
from transformers import AutoModelForTokenClassification, AutoTokenizer


DEFAULT_CONFIG = Path("config.yaml")


@dataclass(frozen=True)
class NerSentence:
    """A token-label sentence from CoNLL data."""

    tokens: list[str]
    labels: list[str]


@dataclass(frozen=True)
class PredictionRecord:
    """Gold and predicted labels for one sentence."""

    tokens: list[str]
    gold_labels: list[str]
    predicted_labels: list[str]


def load_config(path: Path) -> dict:
    """Load project configuration."""
    with path.open("r", encoding="utf-8") as file:
        return yaml.safe_load(file)


def read_conll(path: Path) -> list[NerSentence]:
    """Read CoNLL token-label sentences."""
    sentences: list[NerSentence] = []
    tokens: list[str] = []
    labels: list[str] = []

    with path.open("r", encoding="utf-8") as file:
        for raw_line in file:
            line = raw_line.strip()
            if not line:
                if tokens:
                    sentences.append(NerSentence(tokens=tokens, labels=labels))
                    tokens = []
                    labels = []
                continue

            token, label = line.rsplit(" ", 1)
            tokens.append(token)
            labels.append(label)

    if tokens:
        sentences.append(NerSentence(tokens=tokens, labels=labels))

    return sentences


def predict_batch(
    model,
    tokenizer,
    sentences: list[NerSentence],
    device: torch.device,
    max_length: int,
) -> list[list[str]]:
    """Predict word-level labels for a batch of sentences."""
    encoded = tokenizer(
        [sentence.tokens for sentence in sentences],
        is_split_into_words=True,
        padding=True,
        truncation=True,
        max_length=max_length,
        return_tensors="pt",
    )
    encoded = {key: value.to(device) for key, value in encoded.items()}

    with torch.no_grad():
        logits = model(**encoded).logits
        prediction_ids = logits.argmax(dim=-1).cpu().tolist()

    batch_predictions: list[list[str]] = []
    for batch_index, sentence in enumerate(sentences):
        word_ids = tokenizer(
            sentence.tokens,
            is_split_into_words=True,
            truncation=True,
            max_length=max_length,
        ).word_ids()
        predictions = ["O"] * len(sentence.tokens)
        seen_words: set[int] = set()

        for token_index, word_id in enumerate(word_ids):
            if word_id is None or word_id in seen_words:
                continue
            if word_id < len(predictions):
                predictions[word_id] = model.config.id2label[int(prediction_ids[batch_index][token_index])]
                seen_words.add(word_id)

        batch_predictions.append(predictions)

    return batch_predictions


def predict_dataset(
    model,
    tokenizer,
    sentences: list[NerSentence],
    batch_size: int,
    max_length: int,
) -> list[PredictionRecord]:
    """Predict labels for all sentences."""
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)
    model.eval()

    records: list[PredictionRecord] = []
    for start in range(0, len(sentences), batch_size):
        batch = sentences[start : start + batch_size]
        predicted_batch = predict_batch(model, tokenizer, batch, device, max_length)
        for sentence, predicted_labels in zip(batch, predicted_batch, strict=True):
            records.append(
                PredictionRecord(
                    tokens=sentence.tokens,
                    gold_labels=sentence.labels,
                    predicted_labels=predicted_labels,
                )
            )

    return records


def flatten_labels(records: list[PredictionRecord]) -> tuple[list[str], list[str]]:
    """Flatten gold and predicted labels for token-level analysis."""
    gold: list[str] = []
    predicted: list[str] = []
    for record in records:
        gold.extend(record.gold_labels)
        predicted.extend(record.predicted_labels)
    return gold, predicted


def write_confusion_matrix(records: list[PredictionRecord], labels: list[str], path: Path) -> None:
    """Write token-level confusion matrix as CSV."""
    path.parent.mkdir(parents=True, exist_ok=True)
    gold, predicted = flatten_labels(records)
    matrix = confusion_matrix(gold, predicted, labels=labels)

    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["gold\\predicted", *labels])
        for label, row in zip(labels, matrix, strict=True):
            writer.writerow([label, *row.tolist()])


def write_examples(records: list[PredictionRecord], path: Path, limit: int = 20) -> None:
    """Write correct and incorrect prediction examples as JSONL."""
    path.parent.mkdir(parents=True, exist_ok=True)
    correct = [record for record in records if record.gold_labels == record.predicted_labels][:limit]
    incorrect = [record for record in records if record.gold_labels != record.predicted_labels][:limit]

    with path.open("w", encoding="utf-8") as file:
        for status, selected_records in (("correct", correct), ("incorrect", incorrect)):
            for record in selected_records:
                payload = {
                    "status": status,
                    "tokens": record.tokens,
                    "gold_labels": record.gold_labels,
                    "predicted_labels": record.predicted_labels,
                }
                file.write(json.dumps(payload, ensure_ascii=False) + "\n")


def summarize_predictions(records: list[PredictionRecord]) -> dict:
    """Return aggregate evaluation metrics."""
    y_true = [record.gold_labels for record in records]
    y_pred = [record.predicted_labels for record in records]
    gold_flat, predicted_flat = flatten_labels(records)
    mismatches = sum(gold != predicted for gold, predicted in zip(gold_flat, predicted_flat, strict=True))
    exact_matches = sum(record.gold_labels == record.predicted_labels for record in records)

    return {
        "sentence_count": len(records),
        "token_count": len(gold_flat),
        "token_mismatches": mismatches,
        "token_accuracy": (len(gold_flat) - mismatches) / max(len(gold_flat), 1),
        "sentence_exact_match": exact_matches / max(len(records), 1),
        "micro_precision": precision_score(y_true, y_pred, zero_division=0),
        "micro_recall": recall_score(y_true, y_pred, zero_division=0),
        "micro_f1": f1_score(y_true, y_pred, zero_division=0),
        "seqeval_report": classification_report(y_true, y_pred, output_dict=True, zero_division=0),
        "gold_label_counts": dict(Counter(gold_flat)),
        "predicted_label_counts": dict(Counter(predicted_flat)),
    }


def write_json_report(summary: dict, path: Path) -> None:
    """Write full metrics as JSON."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(summary, indent=2, ensure_ascii=False, default=json_default), encoding="utf-8")


def json_default(value):
    """Convert numpy scalar values to JSON-compatible Python values."""
    if isinstance(value, np.integer):
        return int(value)
    if isinstance(value, np.floating):
        return float(value)
    raise TypeError(f"Object of type {value.__class__.__name__} is not JSON serializable")


def write_markdown_report(summary: dict, model_dir: str, path: Path) -> None:
    """Write human-readable Phase 4 report."""
    path.parent.mkdir(parents=True, exist_ok=True)
    report = summary["seqeval_report"]
    entity_names = [key for key in report if key not in {"micro avg", "macro avg", "weighted avg"}]

    rows = []
    for entity in sorted(entity_names):
        metrics = report[entity]
        rows.append(
            "| {entity} | {precision:.4f} | {recall:.4f} | {f1:.4f} | {support} |".format(
                entity=entity,
                precision=metrics["precision"],
                recall=metrics["recall"],
                f1=metrics["f1-score"],
                support=int(metrics["support"]),
            )
        )

    content = f"""# Phase 4 Evaluation Report

Generated at: {datetime.now(timezone.utc).isoformat()}

## Model

- Model directory: {model_dir}
- Test file: data/annotated/test.conll

## Overall Metrics

- Sentences: {summary["sentence_count"]}
- Tokens: {summary["token_count"]}
- Token accuracy: {summary["token_accuracy"]:.4f}
- Sentence exact match: {summary["sentence_exact_match"]:.4f}
- Micro precision: {summary["micro_precision"]:.4f}
- Micro recall: {summary["micro_recall"]:.4f}
- Micro F1: {summary["micro_f1"]:.4f}

## Metrics per Entity

| Entity | Precision | Recall | F1 | Support |
| --- | ---: | ---: | ---: | ---: |
{chr(10).join(rows)}

## Artifacts

- Full metrics JSON: reports/evaluation_metrics.json
- Token-level confusion matrix: reports/confusion_matrix.csv
- Correct and incorrect examples: reports/prediction_examples.jsonl

## Caveat

These metrics evaluate the Phase 3 bootstrap model against the semi-automatic
Phase 2 labels. They are useful for engineering progress, but final claims still
need manually reviewed labels.
"""
    path.write_text(content, encoding="utf-8")


def evaluate_from_config(config: dict) -> dict:
    """Load model and test data, then run evaluation."""
    data_config = config["data"]
    model_dir = config["model"]["output_dir"]
    batch_size = int(config["training"]["per_device_eval_batch_size"])
    max_length = int(config["training"].get("max_length", 128))

    sentences = read_conll(Path(data_config["test_file"]))
    tokenizer = AutoTokenizer.from_pretrained(model_dir)
    model = AutoModelForTokenClassification.from_pretrained(model_dir)
    records = predict_dataset(model, tokenizer, sentences, batch_size, max_length)
    summary = summarize_predictions(records)

    write_json_report(summary, Path("reports/evaluation_metrics.json"))
    write_confusion_matrix(records, config["labels"], Path("reports/confusion_matrix.csv"))
    write_examples(records, Path("reports/prediction_examples.jsonl"))
    write_markdown_report(summary, model_dir, Path("reports/evaluation_report.md"))
    return summary


def main() -> None:
    """CLI entry point."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG, help="Path to config.yaml")
    args = parser.parse_args()

    summary = evaluate_from_config(load_config(args.config))
    print(f"Micro F1: {summary['micro_f1']:.4f}")
    print("Saved evaluation artifacts to reports/")


if __name__ == "__main__":
    main()
