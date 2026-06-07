"""Fine-tune transformer models for Indonesian medical NER token classification."""

from __future__ import annotations

import argparse
import json
import random
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

import numpy as np
import torch
import yaml
from torch.utils.data import DataLoader
from tqdm.auto import tqdm
from transformers import AutoConfig, AutoModelForTokenClassification, AutoTokenizer, get_linear_schedule_with_warmup


DEFAULT_CONFIG = Path("config.yaml")
IGNORE_INDEX = -100


@dataclass(frozen=True)
class NerSentence:
    """A tokenized NER sentence from a CoNLL file."""

    tokens: list[str]
    labels: list[str]


def load_config(path: Path) -> dict:
    """Load YAML project configuration."""
    with path.open("r", encoding="utf-8") as file:
        return yaml.safe_load(file)


def set_seed(seed: int) -> None:
    """Set random seeds for reproducible training."""
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)


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


def limit_samples(sentences: list[NerSentence], max_samples: int | None) -> list[NerSentence]:
    """Return at most max_samples sentences when a limit is configured."""
    if max_samples is None or max_samples <= 0:
        return sentences
    return sentences[:max_samples]


def align_labels(
    sentence: NerSentence,
    tokenizer,
    label_to_id: dict[str, int],
    max_length: int,
) -> dict[str, list[int]]:
    """Tokenize a sentence and align word-level labels to first subtokens."""
    encoded = tokenizer(
        sentence.tokens,
        is_split_into_words=True,
        truncation=True,
        max_length=max_length,
    )
    word_ids = encoded.word_ids()

    labels: list[int] = []
    previous_word_id: int | None = None
    for word_id in word_ids:
        if word_id is None:
            labels.append(IGNORE_INDEX)
        elif word_id != previous_word_id:
            labels.append(label_to_id[sentence.labels[word_id]])
        else:
            labels.append(IGNORE_INDEX)
        previous_word_id = word_id

    encoded["labels"] = labels
    return encoded


def encode_dataset(
    sentences: Iterable[NerSentence],
    tokenizer,
    label_to_id: dict[str, int],
    max_length: int,
) -> list[dict[str, list[int]]]:
    """Encode all sentences into transformer features."""
    return [align_labels(sentence, tokenizer, label_to_id, max_length) for sentence in sentences]


def make_collate_fn(tokenizer):
    """Create a collate function that pads model inputs and labels together."""

    def collate(features: list[dict[str, list[int]]]) -> dict[str, torch.Tensor]:
        labels = [feature["labels"] for feature in features]
        inputs = [
            {key: value for key, value in feature.items() if key != "labels"}
            for feature in features
        ]
        batch = tokenizer.pad(inputs, padding=True, return_tensors="pt")
        max_length = batch["input_ids"].shape[1]
        padded_labels = [
            label + [IGNORE_INDEX] * (max_length - len(label))
            for label in labels
        ]
        batch["labels"] = torch.tensor(padded_labels, dtype=torch.long)
        return batch

    return collate


def evaluate(model, dataloader: DataLoader, device: torch.device) -> dict[str, float]:
    """Evaluate token-level loss and accuracy on non-ignored labels."""
    model.eval()
    total_loss = 0.0
    total_batches = 0
    correct = 0
    total = 0

    with torch.no_grad():
        for batch in dataloader:
            batch = {key: value.to(device) for key, value in batch.items()}
            outputs = model(**batch)
            total_loss += float(outputs.loss.item())
            total_batches += 1

            predictions = outputs.logits.argmax(dim=-1)
            mask = batch["labels"] != IGNORE_INDEX
            correct += int((predictions[mask] == batch["labels"][mask]).sum().item())
            total += int(mask.sum().item())

    return {
        "loss": total_loss / max(total_batches, 1),
        "token_accuracy": correct / max(total, 1),
    }


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


def train_single_model(config: dict, model_key: str, model_config: dict) -> dict:
    """Run fine-tuning for one configured model and save artifacts."""
    data_config = config["data"]
    train_config = config["training"]

    seed = int(train_config["seed"])
    set_seed(seed)

    labels = config["labels"]
    label_to_id = {label: index for index, label in enumerate(labels)}
    id_to_label = {index: label for label, index in label_to_id.items()}

    tokenizer = AutoTokenizer.from_pretrained(model_config["base_model"])
    model_hf_config = AutoConfig.from_pretrained(model_config["base_model"])
    model_hf_config.id2label = id_to_label
    model_hf_config.label2id = label_to_id
    model_hf_config.num_labels = len(labels)
    model = AutoModelForTokenClassification.from_pretrained(
        model_config["base_model"],
        config=model_hf_config,
    )
    model.config.id2label = id_to_label
    model.config.label2id = label_to_id
    model.config.num_labels = len(labels)

    train_file = data_config["silver_train_file"] if train_config.get("train_data_source") == "silver" else data_config["train_file"]
    validation_file = (
        data_config["silver_validation_file"]
        if train_config.get("train_data_source") == "silver"
        else data_config["validation_file"]
    )

    train_sentences = limit_samples(
        read_conll(Path(train_file)),
        train_config.get("max_train_samples"),
    )
    validation_sentences = limit_samples(
        read_conll(Path(validation_file)),
        train_config.get("max_eval_samples"),
    )

    max_length = int(train_config.get("max_length", 128))
    train_features = encode_dataset(train_sentences, tokenizer, label_to_id, max_length)
    validation_features = encode_dataset(validation_sentences, tokenizer, label_to_id, max_length)

    collate_fn = make_collate_fn(tokenizer)
    train_loader = DataLoader(
        train_features,
        batch_size=int(train_config["per_device_train_batch_size"]),
        shuffle=True,
        collate_fn=collate_fn,
    )
    validation_loader = DataLoader(
        validation_features,
        batch_size=int(train_config["per_device_eval_batch_size"]),
        shuffle=False,
        collate_fn=collate_fn,
    )

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)

    optimizer = torch.optim.AdamW(
        model.parameters(),
        lr=float(train_config["learning_rate"]),
        weight_decay=float(train_config["weight_decay"]),
    )
    epochs = int(train_config["num_train_epochs"])
    total_steps = max(len(train_loader) * epochs, 1)
    scheduler = get_linear_schedule_with_warmup(
        optimizer,
        num_warmup_steps=int(total_steps * float(train_config.get("warmup_ratio", 0.0))),
        num_training_steps=total_steps,
    )

    history: list[dict[str, float | int]] = []
    for epoch in range(epochs):
        model.train()
        running_loss = 0.0
        progress = tqdm(train_loader, desc=f"epoch {epoch + 1}/{epochs}", leave=False)

        for batch in progress:
            batch = {key: value.to(device) for key, value in batch.items()}
            outputs = model(**batch)
            loss = outputs.loss
            loss.backward()

            torch.nn.utils.clip_grad_norm_(model.parameters(), float(train_config.get("max_grad_norm", 1.0)))
            optimizer.step()
            scheduler.step()
            optimizer.zero_grad(set_to_none=True)

            running_loss += float(loss.item())
            progress.set_postfix(loss=f"{loss.item():.4f}")

        validation_metrics = evaluate(model, validation_loader, device)
        history.append(
            {
                "epoch": epoch + 1,
                "train_loss": running_loss / max(len(train_loader), 1),
                "validation_loss": validation_metrics["loss"],
                "validation_token_accuracy": validation_metrics["token_accuracy"],
            }
        )

    output_dir = Path(model_config["output_dir"])
    output_dir.mkdir(parents=True, exist_ok=True)
    model.save_pretrained(output_dir)
    tokenizer.save_pretrained(output_dir)
    normalize_saved_model_config(output_dir, len(labels))

    summary = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "model_key": model_key,
        "display_name": model_config.get("display_name", model_config["base_model"]),
        "role": model_config.get("role", ""),
        "base_model": model_config["base_model"],
        "output_dir": str(output_dir),
        "device": str(device),
        "train_data_source": train_config.get("train_data_source", "annotated"),
        "train_file": train_file,
        "validation_file": validation_file,
        "train_sentences": len(train_sentences),
        "validation_sentences": len(validation_sentences),
        "labels": labels,
        "history": history,
    }
    (output_dir / "training_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary


def train(config: dict, model_key: str | None = None) -> list[dict]:
    """Run fine-tuning for one or all configured models."""
    summaries = []
    for key, model_config in get_model_entries(config, model_key).items():
        summaries.append(train_single_model(config, key, model_config))
    return summaries


def normalize_saved_model_config(output_dir: Path, num_labels: int) -> None:
    """Normalize saved config fields used by this Transformers version."""
    config_path = output_dir / "config.json"
    saved_config = json.loads(config_path.read_text(encoding="utf-8"))
    saved_config["_num_labels"] = num_labels
    config_path.write_text(json.dumps(saved_config, indent=2, sort_keys=True), encoding="utf-8")


def write_report(summaries: list[dict], path: Path) -> None:
    """Write a Markdown report for Phase 3."""
    path.parent.mkdir(parents=True, exist_ok=True)
    sections = []
    comparison_rows = []
    for summary in summaries:
        last_epoch = summary["history"][-1] if summary["history"] else {}
        comparison_rows.append(
            "| {model_key} | {role} | {base_model} | {output_dir} | {train_loss:.4f} | {validation_loss:.4f} | {validation_accuracy:.4f} |".format(
                model_key=summary["model_key"],
                role=summary.get("role", ""),
                base_model=summary["base_model"],
                output_dir=summary["output_dir"],
                train_loss=last_epoch.get("train_loss", 0),
                validation_loss=last_epoch.get("validation_loss", 0),
                validation_accuracy=last_epoch.get("validation_token_accuracy", 0),
            )
        )
        sections.append(
            f"""## {summary["display_name"]} (`{summary["model_key"]}`)

- Role: {summary.get("role", "-")}
- Base model: {summary["base_model"]}
- Output directory: {summary["output_dir"]}
- Device: {summary["device"]}
- Training data source: {summary.get("train_data_source", "annotated")}
- Training file: {summary.get("train_file", "unknown")}
- Validation file: {summary.get("validation_file", "unknown")}
- Train sentences used: {summary["train_sentences"]}
- Validation sentences used: {summary["validation_sentences"]}
- Last train loss: {last_epoch.get("train_loss", 0):.4f}
- Last validation loss: {last_epoch.get("validation_loss", 0):.4f}
- Last validation token accuracy: {last_epoch.get("validation_token_accuracy", 0):.4f}
"""
        )

    content = f"""# Phase 3 Training Summary

Generated at: {datetime.now(timezone.utc).isoformat()}

## Shared Setup

- Labels: {", ".join(summaries[0]["labels"]) if summaries else "-"}
- Data source: {summaries[0].get("train_data_source", "annotated") if summaries else "-"}
- Hyperparameters are read once from `training` in `config.yaml` and reused for every model to keep the comparison fair.

## Model Runs

| Model key | Role | Base model | Output dir | Train loss | Validation loss | Validation token accuracy |
| --- | --- | --- | --- | ---: | ---: | ---: |
{chr(10).join(comparison_rows)}

{chr(10).join(sections)}

## Notes

This is a bootstrap training setup on silver labels. `xlm-roberta-base` has a
larger memory footprint than IndoBERT; if GPU memory is limited, lower
`training.per_device_train_batch_size` and rerun the same config for both
models.
"""
    path.write_text(content, encoding="utf-8")


def main() -> None:
    """CLI entry point."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG, help="Path to config.yaml")
    parser.add_argument("--model-key", default=None, help="Train only one configured model key, e.g. indobert or xlm_roberta")
    args = parser.parse_args()

    summaries = train(load_config(args.config), args.model_key)
    write_report(summaries, Path("reports/model_phase3_training_summary.md"))
    for summary in summaries:
        print(f"Saved {summary['model_key']} model to {summary['output_dir']}")


if __name__ == "__main__":
    main()
