"""Create semi-automatic BIO annotations for Indonesian medical NER.

This script uses a curated lexicon and dosage patterns to bootstrap a CoNLL/BIO
dataset. The output is intended as a first-pass annotation set that can be
reviewed and corrected manually in the next iteration.
"""

from __future__ import annotations

import argparse
import random
import re
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

import yaml


DEFAULT_CONFIG = Path("config.yaml")
DEFAULT_LEXICON = Path("resources/medical_lexicon.yaml")
TOKEN_PATTERN = re.compile(r"\d+(?:[,.]\d+)?|[A-Za-zÀ-ÿ]+(?:[-'][A-Za-zÀ-ÿ]+)*|[^\w\s]", re.UNICODE)
DOSAGE_UNIT_PATTERN = re.compile(r"^(?:mg|mcg|g|gram|ml|cc|iu|tablet|kapsul|sendok|tetes)$", re.IGNORECASE)
DOSAGE_FREQ_PATTERN = re.compile(r"^\d+\s*x$", re.IGNORECASE)
DOSAGE_TIME_WORDS = {"sehari", "hari", "jam", "minggu", "bulan", "sekali", "pagi", "siang", "malam"}
DOSAGE_INSTRUCTION_WORDS = {"sesudah", "sebelum", "setelah", "makan", "minum"}
ENTITY_ORDER = ["GEJALA", "OBAT", "DOSIS", "DIAGNOSIS", "ANATOMI"]
SPLIT_RATIOS = {"train": 0.8, "val": 0.1, "test": 0.1}


@dataclass(frozen=True)
class Token:
    """Token text with character offsets."""

    text: str
    start: int
    end: int


def load_yaml(path: Path | str) -> dict:
    """Load a YAML file."""
    path = Path(path)
    with path.open("r", encoding="utf-8") as file:
        return yaml.safe_load(file)


def tokenize(text: str) -> list[Token]:
    """Tokenize text into words, numbers, and punctuation with offsets."""
    return [Token(match.group(), match.start(), match.end()) for match in TOKEN_PATTERN.finditer(text)]


def phrase_to_tokens(phrase: str) -> tuple[str, ...]:
    """Normalize a lexicon phrase into lowercase token text."""
    return tuple(token.text.casefold() for token in tokenize(phrase))


def load_lexicon(path: Path | str) -> dict[str, list[tuple[str, ...]]]:
    """Load lexicon phrases grouped by entity label."""
    raw = load_yaml(path)
    lexicon: dict[str, list[tuple[str, ...]]] = {}
    for label, phrases in raw.items():
        tokenized = [phrase_to_tokens(phrase) for phrase in phrases]
        lexicon[label] = sorted(set(tokenized), key=len, reverse=True)
    return lexicon


def find_lexicon_spans(tokens: list[Token], lexicon: dict[str, list[tuple[str, ...]]]) -> dict[int, tuple[int, str]]:
    """Find non-overlapping lexicon spans using longest-match priority."""
    lowered = [token.text.casefold() for token in tokens]
    spans: dict[int, tuple[int, str]] = {}
    occupied: set[int] = set()

    candidates: list[tuple[int, int, str]] = []
    for label in ENTITY_ORDER:
        for phrase_tokens in lexicon.get(label, []):
            phrase_len = len(phrase_tokens)
            if phrase_len == 0:
                continue
            for start in range(0, len(tokens) - phrase_len + 1):
                end = start + phrase_len
                if tuple(lowered[start:end]) == phrase_tokens:
                    candidates.append((start, end, label))

    candidates.sort(key=lambda item: (-(item[1] - item[0]), ENTITY_ORDER.index(item[2]), item[0]))
    for start, end, label in candidates:
        if any(index in occupied for index in range(start, end)):
            continue
        spans[start] = (end, label)
        occupied.update(range(start, end))

    return spans


def add_dosage_spans(tokens: list[Token], spans: dict[int, tuple[int, str]]) -> dict[int, tuple[int, str]]:
    """Add DOSIS spans such as 500 mg, 2x sehari, or sesudah makan."""
    occupied = {index for start, (end, _) in spans.items() for index in range(start, end)}
    index = 0
    while index < len(tokens):
        if index in occupied:
            index += 1
            continue

        token = tokens[index].text
        next_token = tokens[index + 1].text if index + 1 < len(tokens) else ""
        next_next = tokens[index + 2].text if index + 2 < len(tokens) else ""

        end = index
        if token.isdigit() and DOSAGE_UNIT_PATTERN.match(next_token):
            end = index + 2
        elif DOSAGE_FREQ_PATTERN.match(token):
            end = index + 1
            while end < len(tokens) and tokens[end].text.casefold() in DOSAGE_TIME_WORDS:
                end += 1
        elif token.isdigit() and next_token.casefold() in {"kali", "x"}:
            end = index + 2
            while end < len(tokens) and tokens[end].text.casefold() in DOSAGE_TIME_WORDS:
                end += 1
        elif token.casefold() in DOSAGE_INSTRUCTION_WORDS and next_token.casefold() in DOSAGE_INSTRUCTION_WORDS | {"makan"}:
            end = index + 2
            if next_next.casefold() == "makan":
                end = index + 3

        if end > index and not any(pos in occupied for pos in range(index, end)):
            spans[index] = (end, "DOSIS")
            occupied.update(range(index, end))
            index = end
        else:
            index += 1

    return spans


def annotate_tokens(tokens: list[Token], lexicon: dict[str, list[tuple[str, ...]]]) -> list[str]:
    """Assign BIO labels to tokens."""
    labels = ["O"] * len(tokens)
    spans = add_dosage_spans(tokens, find_lexicon_spans(tokens, lexicon))

    for start, (end, label) in sorted(spans.items()):
        labels[start] = f"B-{label}"
        for index in range(start + 1, end):
            labels[index] = f"I-{label}"

    return labels


def read_corpus(path: Path) -> list[str]:
    """Read non-empty clean corpus lines."""
    with path.open("r", encoding="utf-8") as file:
        return [line.strip() for line in file if line.strip()]


def split_records(records: list[tuple[list[Token], list[str]]], seed: int) -> dict[str, list[tuple[list[Token], list[str]]]]:
    """Shuffle and split records into train/val/test."""
    shuffled = records[:]
    random.Random(seed).shuffle(shuffled)

    train_end = int(len(shuffled) * SPLIT_RATIOS["train"])
    val_end = train_end + int(len(shuffled) * SPLIT_RATIOS["val"])
    return {
        "train": shuffled[:train_end],
        "val": shuffled[train_end:val_end],
        "test": shuffled[val_end:],
    }


def write_conll(records: Iterable[tuple[list[Token], list[str]]], path: Path) -> None:
    """Write token-label pairs in CoNLL format."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as file:
        for tokens, labels in records:
            for token, label in zip(tokens, labels, strict=True):
                file.write(f"{token.text} {label}\n")
            file.write("\n")


def count_entities(records: Iterable[tuple[list[Token], list[str]]]) -> Counter[str]:
    """Count B- labels by entity type."""
    counts: Counter[str] = Counter()
    for _, labels in records:
        for label in labels:
            if label.startswith("B-"):
                counts[label[2:]] += 1
    return counts


def write_report(splits: dict[str, list[tuple[list[Token], list[str]]]], path: Path) -> None:
    """Write Phase 2 annotation summary."""
    path.parent.mkdir(parents=True, exist_ok=True)
    total_records = sum(len(records) for records in splits.values())
    total_tokens = sum(len(tokens) for records in splits.values() for tokens, _ in records)
    lines = [
        "# Phase 2 Annotation Summary",
        "",
        f"Generated at: {datetime.now(timezone.utc).isoformat()}",
        "",
        "## Method",
        "",
        "- Tokenized the clean corpus with a deterministic regex tokenizer.",
        "- Applied longest-match lexicon annotation for GEJALA, OBAT, DIAGNOSIS, and ANATOMI.",
        "- Applied regex/rule annotation for DOSIS patterns.",
        "- Split records deterministically into train/val/test with seed 42.",
        "",
        "## Caveat",
        "",
        "This is a semi-automatic bootstrap dataset and should be manually reviewed before final model claims.",
        "",
        "## Result",
        "",
        f"- Total records: {total_records}",
        f"- Total tokens: {total_tokens}",
        "",
        "## Split Counts",
        "",
        "| Split | Records | Tokens | GEJALA | OBAT | DOSIS | DIAGNOSIS | ANATOMI |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]

    for split_name, records in splits.items():
        entity_counts = count_entities(records)
        token_count = sum(len(tokens) for tokens, _ in records)
        lines.append(
            "| {split} | {records} | {tokens} | {gejala} | {obat} | {dosis} | {diagnosis} | {anatomi} |".format(
                split=split_name,
                records=len(records),
                tokens=token_count,
                gejala=entity_counts["GEJALA"],
                obat=entity_counts["OBAT"],
                dosis=entity_counts["DOSIS"],
                diagnosis=entity_counts["DIAGNOSIS"],
                anatomi=entity_counts["ANATOMI"],
            )
        )

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_annotations(corpus_path: Path, lexicon_path: Path) -> list[tuple[list[Token], list[str]]]:
    """Create BIO annotations from corpus text."""
    lexicon = load_lexicon(lexicon_path)
    annotated = []
    for text in read_corpus(corpus_path):
        tokens = tokenize(text)
        labels = annotate_tokens(tokens, lexicon)
        annotated.append((tokens, labels))
    return annotated


def main() -> None:
    """Build train/val/test CoNLL files from the clean corpus."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG, help="Path to config.yaml")
    parser.add_argument("--lexicon", type=Path, default=DEFAULT_LEXICON, help="Path to medical lexicon YAML")
    args = parser.parse_args()

    config = load_yaml(args.config)
    data_config = config["data"]
    seed = int(config["training"]["seed"])

    annotated = build_annotations(Path(data_config["clean_file"]), args.lexicon)
    splits = split_records(annotated, seed)

    write_conll(splits["train"], Path(data_config["train_file"]))
    write_conll(splits["val"], Path(data_config["validation_file"]))
    write_conll(splits["test"], Path(data_config["test_file"]))
    write_report(splits, Path("reports/data_phase2_annotation_summary.md"))

    print(
        "Wrote BIO splits: "
        f"train={len(splits['train'])}, val={len(splits['val'])}, test={len(splits['test'])}"
    )


if __name__ == "__main__":
    main()
