"""Collect and clean Indonesian medical text for NER annotation.

The default source is a public Hugging Face dataset of Indonesian health
questions. If the source cannot be loaded, this script writes a small fallback
corpus so the rest of the project remains runnable.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

import yaml
from datasets import Dataset, DatasetDict, load_dataset


DEFAULT_CONFIG = Path("config.yaml")


@dataclass(frozen=True)
class CleanRecord:
    """A single cleaned text record with source metadata."""

    record_id: str
    text: str
    source: str
    intent: str | int | None = None


FALLBACK_TEXTS = [
    "Pasien mengalami demam tinggi, batuk, dan nyeri tenggorokan sejak dua hari.",
    "Dokter memberikan paracetamol 500 mg diminum tiga kali sehari setelah makan.",
    "Keluhan sesak napas disertai nyeri dada sebelah kiri perlu evaluasi lebih lanjut.",
    "Riwayat hipertensi dan diabetes melitus dicatat pada kunjungan sebelumnya.",
    "Pasien merasa mual, nyeri ulu hati, dan perut kembung setelah makan pedas.",
]


def load_config(path: Path) -> dict:
    """Load project configuration from YAML."""
    with path.open("r", encoding="utf-8") as file:
        return yaml.safe_load(file)


def normalize_text(text: str) -> str:
    """Normalize whitespace and punctuation spacing without changing casing."""
    text = str(text)
    text = text.replace("\u00a0", " ")
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"\s+([,.;:!?])", r"\1", text)
    return text.strip()


def iter_dataset_records(dataset: Dataset | DatasetDict, text_column: str, source: str) -> Iterable[CleanRecord]:
    """Yield clean candidate records from a Hugging Face dataset."""
    split = dataset["train"] if isinstance(dataset, DatasetDict) else dataset
    for index, row in enumerate(split):
        text = normalize_text(row.get(text_column, ""))
        if not text:
            continue
        yield CleanRecord(
            record_id=f"{source.replace('/', '_')}_{index:06d}",
            text=text,
            source=source,
            intent=row.get("intent"),
        )


def fallback_records() -> list[CleanRecord]:
    """Return a small local corpus for offline or source-failure scenarios."""
    return [
        CleanRecord(
            record_id=f"fallback_{index:03d}",
            text=normalize_text(text),
            source="local_fallback",
            intent=None,
        )
        for index, text in enumerate(FALLBACK_TEXTS)
    ]


def deduplicate_records(records: Iterable[CleanRecord]) -> list[CleanRecord]:
    """Remove duplicate texts while preserving first occurrence order."""
    seen: set[str] = set()
    deduped: list[CleanRecord] = []

    for record in records:
        key = record.text.casefold()
        if key in seen:
            continue
        seen.add(key)
        deduped.append(record)

    return deduped


def write_raw_jsonl(records: Iterable[CleanRecord], path: Path) -> None:
    """Write raw-ish records as JSONL for traceability."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file:
        for record in records:
            payload = {
                "id": record.record_id,
                "text": record.text,
                "source": record.source,
                "intent": record.intent,
            }
            file.write(json.dumps(payload, ensure_ascii=False) + "\n")


def write_clean_corpus(records: Iterable[CleanRecord], path: Path) -> None:
    """Write one cleaned text per line for annotation preparation."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as file:
        for record in records:
            file.write(record.text + "\n")


def write_metadata(records: Iterable[CleanRecord], path: Path) -> None:
    """Write metadata for each clean corpus row."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=["id", "source", "intent", "text"])
        writer.writeheader()
        for record in records:
            writer.writerow(
                {
                    "id": record.record_id,
                    "source": record.source,
                    "intent": record.intent,
                    "text": record.text,
                }
            )


def write_report(records: list[CleanRecord], source_name: str, path: Path) -> None:
    """Write a compact Phase 1 corpus summary."""
    path.parent.mkdir(parents=True, exist_ok=True)
    lengths = [len(record.text.split()) for record in records]
    avg_tokens = sum(lengths) / len(lengths) if lengths else 0
    source_counts: dict[str, int] = {}
    for record in records:
        source_counts[record.source] = source_counts.get(record.source, 0) + 1

    source_lines = "\n".join(f"- {source}: {count}" for source, count in sorted(source_counts.items()))
    content = f"""# Phase 1 Data Summary

Generated at: {datetime.now(timezone.utc).isoformat()}

## Source

- Primary dataset: {source_name}
- Output corpus: data/clean/medical_text_corpus.txt
- Metadata: data/clean/medical_text_corpus_metadata.csv

## Cleaning

- Normalized whitespace.
- Removed empty texts.
- Removed exact duplicate texts case-insensitively.
- Preserved original casing because clinical terms and medicine names can carry useful cues.

## Result

- Clean records: {len(records)}
- Average whitespace-token count: {avg_tokens:.2f}

## Records by source

{source_lines}

## Next Phase

Use `data/clean/medical_text_corpus.txt` as the input corpus for BIO annotation.
"""
    path.write_text(content, encoding="utf-8")


def build_corpus(config: dict) -> list[CleanRecord]:
    """Load the configured dataset and return cleaned, deduplicated records."""
    data_config = config["data"]
    source_dataset = data_config["source_dataset"]
    text_column = data_config["text_column"]

    try:
        dataset = load_dataset(source_dataset)
        records = list(iter_dataset_records(dataset, text_column, source_dataset))
    except Exception as exc:
        print(f"WARNING: failed to load {source_dataset}: {exc}")
        records = fallback_records()

    return deduplicate_records(records)


def main() -> None:
    """Collect, clean, deduplicate, and save the Phase 1 corpus."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG, help="Path to config.yaml")
    args = parser.parse_args()

    config = load_config(args.config)
    data_config = config["data"]
    records = build_corpus(config)

    write_raw_jsonl(records, Path(data_config["raw_file"]))
    write_clean_corpus(records, Path(data_config["clean_file"]))
    write_metadata(records, Path(data_config["metadata_file"]))
    write_report(records, data_config["source_dataset"], Path("reports/data_phase1_summary.md"))

    print(f"Wrote {len(records)} clean records to {data_config['clean_file']}")


if __name__ == "__main__":
    main()
