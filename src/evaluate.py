"""Evaluate trained Indonesian medical NER models and compare them."""

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


def get_model_entries(config: dict, model_key: str | None = None) -> dict[str, dict]:
    """Return configured model entries, with backward compatibility for old config."""
    if "models" in config:
        models = config["models"]
    else:
        models = {
            "default": {
                "display_name": config["model"]["base_model"],
                "role": "utama",
                "base_model": config["model"]["base_model"],
                "output_dir": config["model"]["output_dir"],
            }
        }

    if model_key:
        if model_key not in models:
            valid = ", ".join(sorted(models))
            raise KeyError(f"Unknown model key '{model_key}'. Valid options: {valid}")
        return {model_key: models[model_key]}
    return models


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


def write_markdown_report(
    summary: dict,
    model_dir: str,
    test_file: str,
    report_prefix: str,
    path: Path,
    model_name: str = "",
) -> None:
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

- Model name: {model_name or model_dir}
- Model directory: {model_dir}
- Test file: {test_file}

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

- Full metrics JSON: reports/{report_prefix}_metrics.json
- Token-level confusion matrix: reports/{report_prefix}_confusion_matrix.csv
- Correct and incorrect examples: reports/{report_prefix}_prediction_examples.jsonl

## Caveat

These metrics evaluate the Phase 3 bootstrap model against the semi-automatic
Phase 2 labels. They are useful for engineering progress, but final claims still
need manually reviewed labels.
"""
    path.write_text(content, encoding="utf-8")


def evaluate_model(
    config: dict,
    model_key: str,
    model_config: dict,
    test_file: Path | None = None,
    report_prefix: str | None = None,
) -> dict:
    """Load one model and test data, then run evaluation."""
    data_config = config["data"]
    model_dir = model_config["output_dir"]
    batch_size = int(config["training"]["per_device_eval_batch_size"])
    max_length = int(config["training"].get("max_length", 128))
    test_path = test_file or Path(data_config["test_file"])
    prefix = report_prefix or f"evaluation_{model_key}"

    sentences = read_conll(test_path)
    tokenizer = AutoTokenizer.from_pretrained(model_dir)
    model = AutoModelForTokenClassification.from_pretrained(model_dir)
    records = predict_dataset(model, tokenizer, sentences, batch_size, max_length)
    summary = summarize_predictions(records)
    summary["model_key"] = model_key
    summary["model_name"] = model_config.get("display_name", model_config["base_model"])
    summary["role"] = model_config.get("role", "")
    summary["base_model"] = model_config["base_model"]
    summary["model_dir"] = model_dir
    summary["test_file"] = str(test_path)

    write_json_report(summary, Path(f"reports/{prefix}_metrics.json"))
    write_confusion_matrix(records, config["labels"], Path(f"reports/{prefix}_confusion_matrix.csv"))
    write_examples(records, Path(f"reports/{prefix}_prediction_examples.jsonl"))
    write_markdown_report(
        summary,
        model_dir,
        str(test_path),
        prefix,
        Path(f"reports/{prefix}_report.md"),
        summary["model_name"],
    )
    return summary


def entity_f1(summary: dict, entity: str) -> float | None:
    """Return seqeval F1 for one entity if present."""
    metrics = summary["seqeval_report"].get(entity)
    if not metrics:
        return None
    return float(metrics["f1-score"])


def f1_bar(value: float | None, width: int = 20) -> str:
    """Render a compact text bar for Markdown reports."""
    if value is None:
        return ""
    filled = round(value * width)
    return "#" * filled + "-" * (width - filled)


def write_comparison_reports(summaries: list[dict], labels: list[str], path: Path) -> None:
    """Write side-by-side model comparison artifacts."""
    path.parent.mkdir(parents=True, exist_ok=True)
    entity_names = sorted({label.split("-", 1)[1] for label in labels if label != "O" and "-" in label})

    csv_path = path.with_suffix(".csv")
    with csv_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["entity", *[summary["model_key"] for summary in summaries]])
        for entity in entity_names:
            writer.writerow([entity, *[entity_f1(summary, entity) for summary in summaries]])

    header = "| Entity | " + " | ".join(f"{summary['model_key']} F1" for summary in summaries) + " |"
    divider = "| --- | " + " | ".join("---:" for _ in summaries) + " |"
    rows = []
    graph_rows = []
    for entity in entity_names:
        values = [entity_f1(summary, entity) for summary in summaries]
        rows.append(
            "| {entity} | {values} |".format(
                entity=entity,
                values=" | ".join("" if value is None else f"{value:.4f}" for value in values),
            )
        )
        graph_rows.extend(
            f"- {entity} / {summary['model_key']}: `{f1_bar(value)}` {value:.4f}"
            for summary, value in zip(summaries, values, strict=True)
            if value is not None
        )

    overall_rows = [
        "| {model_key} | {role} | {base_model} | {model_dir} | {precision:.4f} | {recall:.4f} | {f1:.4f} |".format(
            model_key=summary["model_key"],
            role=summary.get("role", ""),
            base_model=summary["base_model"],
            model_dir=summary["model_dir"],
            precision=summary["micro_precision"],
            recall=summary["micro_recall"],
            f1=summary["micro_f1"],
        )
        for summary in summaries
    ]

    content = f"""# Phase 4 Model Comparison

Generated at: {datetime.now(timezone.utc).isoformat()}

## Overall Metrics

| Model key | Role | Base model | Model dir | Micro precision | Micro recall | Micro F1 |
| --- | --- | --- | --- | ---: | ---: | ---: |
{chr(10).join(overall_rows)}

## F1 per Entity

{header}
{divider}
{chr(10).join(rows)}

## Compact F1 Chart

{chr(10).join(graph_rows)}

## Trade-off Notes

- `indobert` is the primary Indonesian model and is expected to be lighter for this Bahasa Indonesia-only task.
- `xlm_roberta` is the multilingual comparator. It is larger and can need a smaller batch size on limited GPU memory.
- Use the same data split and hyperparameters for both runs before making the comparison table final.

## Artifacts

- CSV comparison table: `{csv_path.as_posix()}`
- Per-model JSON, confusion matrix, examples, and Markdown reports are stored with `reports/evaluation_<model_key>_*` names.
"""
    path.write_text(content, encoding="utf-8")


def evaluate_from_config(
    config: dict,
    test_file: Path | None = None,
    report_prefix: str = "evaluation",
    model_key: str | None = None,
) -> list[dict]:
    """Evaluate one or all configured models."""
    summaries = []
    for key, model_config in get_model_entries(config, model_key).items():
        prefix = report_prefix if model_key else f"{report_prefix}_{key}"
        summaries.append(evaluate_model(config, key, model_config, test_file, prefix))

    if len(summaries) > 1:
        write_comparison_reports(summaries, config["labels"], Path("reports/model_comparison.md"))
    return summaries


def main() -> None:
    """CLI entry point."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG, help="Path to config.yaml")
    parser.add_argument("--test-file", type=Path, default=None, help="Optional CoNLL test file override")
    parser.add_argument("--report-prefix", default="evaluation", help="Prefix for report artifact filenames")
    parser.add_argument("--model-key", default=None, help="Evaluate only one configured model key, e.g. indobert or xlm_roberta")
    args = parser.parse_args()

    summaries = evaluate_from_config(load_config(args.config), args.test_file, args.report_prefix, args.model_key)
    for summary in summaries:
        print(f"{summary['model_key']} Micro F1: {summary['micro_f1']:.4f}")
    print("Saved evaluation artifacts to reports/")


if __name__ == "__main__":
    main()
