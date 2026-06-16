"""Build expanded-label silver data aligned with Phase 9 adjudication policy."""

from __future__ import annotations

import argparse
import json
import random
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from annotate_bio import Token
from prepare_phase9_challenge_set import (
    ENTITY_TYPES,
    annotate_text,
    build_phrase_index,
    read_lines,
    read_sample_texts,
)


DEFAULT_CORPUS = Path("data/clean/medical_text_corpus.txt")
DEFAULT_TRUE_GOLD_TEXTS = Path("data/true_gold_300/sample_texts.tsv")
DEFAULT_PHASE9_TEXTS = Path("data/phase9_challenge_set/sample_texts.tsv")
DEFAULT_OUTPUT_DIR = Path("data/phase9_expanded_silver")
SPLIT_RATIOS = {"train": 0.9, "val": 0.1}


def write_conll(records: list[tuple[list[Token], list[str]]], path: Path) -> None:
    """Write CoNLL token-label pairs without comment lines."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as file:
        for tokens, labels in records:
            for token, label in zip(tokens, labels, strict=True):
                file.write(f"{token.text} {label}\n")
            file.write("\n")


def split_records(records: list[tuple[list[Token], list[str]]], seed: int) -> dict[str, list[tuple[list[Token], list[str]]]]:
    """Shuffle and split records."""
    shuffled = records[:]
    random.Random(seed).shuffle(shuffled)
    train_end = int(len(shuffled) * SPLIT_RATIOS["train"])
    return {"train": shuffled[:train_end], "val": shuffled[train_end:]}


def count_entities(records: list[tuple[list[Token], list[str]]]) -> Counter[str]:
    """Count entity starts by type."""
    counts: Counter[str] = Counter()
    for _, labels in records:
        for label in labels:
            if label.startswith("B-"):
                counts[label[2:]] += 1
    return counts


def write_manifest(
    output_dir: Path,
    records_total: int,
    excluded_true_gold: int,
    excluded_phase9: int,
    splits: dict[str, list[tuple[list[Token], list[str]]]],
) -> None:
    """Write machine-readable dataset metadata."""
    manifest = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "dataset_type": "phase9_expanded_silver",
        "annotation_source": "rules_following_phase9_human_adjudication_policy",
        "human_annotated": False,
        "human_gold": False,
        "true_gold_texts_excluded": excluded_true_gold,
        "phase9_challenge_texts_excluded": excluded_phase9,
        "records_after_exclusion": records_total,
        "entity_types": ENTITY_TYPES,
        "files": {
            "train": str(output_dir / "train.conll"),
            "validation": str(output_dir / "val.conll"),
        },
        "split_counts": {name: len(records) for name, records in splits.items()},
        "entity_counts": {name: dict(count_entities(records)) for name, records in splits.items()},
    }
    (output_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")


def write_report(
    output_dir: Path,
    records_total: int,
    excluded_true_gold: int,
    excluded_phase9: int,
    splits: dict[str, list[tuple[list[Token], list[str]]]],
) -> None:
    """Write a reviewer-friendly dataset report."""
    header = "| Split | Records | " + " | ".join(ENTITY_TYPES) + " |"
    divider = "| --- | ---: | " + " | ".join("---:" for _ in ENTITY_TYPES) + " |"
    rows = []
    for split_name, records in splits.items():
        counts = count_entities(records)
        rows.append(
            "| {split} | {records} | {counts} |".format(
                split=split_name,
                records=len(records),
                counts=" | ".join(str(counts[entity]) for entity in ENTITY_TYPES),
            )
        )

    content = f"""# Phase 9 Expanded Silver Dataset

Generated at: {datetime.now(timezone.utc).isoformat()}

## Status

This dataset is automatically labeled with rules aligned to Phase 9 human
adjudication decisions. It is intended for retraining an expanded-label model,
not for final evaluation.

The true gold and Phase 9 challenge texts are excluded from training data.

## Counts

- Excluded true-gold texts: {excluded_true_gold}
- Excluded Phase 9 challenge texts: {excluded_phase9}
- Records after exclusion: {records_total}

## Split Counts

{header}
{divider}
{chr(10).join(rows)}
"""
    (output_dir / "README.md").write_text(content, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--corpus", type=Path, default=DEFAULT_CORPUS)
    parser.add_argument("--true-gold-texts", type=Path, default=DEFAULT_TRUE_GOLD_TEXTS)
    parser.add_argument("--phase9-texts", type=Path, default=DEFAULT_PHASE9_TEXTS)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    corpus = read_lines(args.corpus)
    true_gold_texts = read_sample_texts(args.true_gold_texts)
    phase9_texts = read_sample_texts(args.phase9_texts)
    excluded = true_gold_texts | phase9_texts
    filtered = [text for text in corpus if text.casefold() not in excluded]

    phrase_index = build_phrase_index()
    records = [annotate_text(text, phrase_index) for text in filtered]
    splits = split_records(records, args.seed)

    args.output_dir.mkdir(parents=True, exist_ok=True)
    write_conll(splits["train"], args.output_dir / "train.conll")
    write_conll(splits["val"], args.output_dir / "val.conll")
    write_manifest(args.output_dir, len(records), len(true_gold_texts), len(phase9_texts), splits)
    write_report(args.output_dir, len(records), len(true_gold_texts), len(phase9_texts), splits)
    print(
        "Wrote Phase 9 expanded silver splits: "
        f"train={len(splits['train'])}, val={len(splits['val'])}, "
        f"excluded={len(corpus) - len(filtered)}"
    )


if __name__ == "__main__":
    main()
