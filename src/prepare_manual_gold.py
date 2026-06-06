"""Prepare a manual gold-test annotation package for two annotators."""

from __future__ import annotations

import argparse
import random
from datetime import datetime, timezone
from pathlib import Path

import yaml

from annotate_bio import tokenize


DEFAULT_CONFIG = Path("config.yaml")
DEFAULT_OUTPUT_DIR = Path("data/manual_gold")
ALLOWED_LABELS = [
    "O",
    "B-GEJALA",
    "I-GEJALA",
    "B-OBAT",
    "I-OBAT",
    "B-DOSIS",
    "I-DOSIS",
    "B-DIAGNOSIS",
    "I-DIAGNOSIS",
    "B-ANATOMI",
    "I-ANATOMI",
]


def load_config(path: Path) -> dict:
    """Load project YAML configuration."""
    with path.open("r", encoding="utf-8") as file:
        return yaml.safe_load(file)


def read_corpus(path: Path) -> list[str]:
    """Read non-empty corpus lines."""
    with path.open("r", encoding="utf-8") as file:
        return [line.strip() for line in file if line.strip()]


def write_annotation_template(texts: list[str], path: Path) -> None:
    """Write a CoNLL annotation template initialized with O labels."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as file:
        for text in texts:
            file.write(f"# text = {text}\n")
            for token in tokenize(text):
                file.write(f"{token.text} O\n")
            file.write("\n")


def write_sample_texts(texts: list[str], path: Path) -> None:
    """Write sampled texts as a reviewer-friendly text file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as file:
        for index, text in enumerate(texts, start=1):
            file.write(f"{index}\t{text}\n")


def write_instructions(output_dir: Path, sample_size: int) -> None:
    """Write manual annotation instructions."""
    content = f"""# Manual Gold Test Annotation Instructions

Generated at: {datetime.now(timezone.utc).isoformat()}

## Purpose

This package contains {sample_size} sampled Indonesian medical texts for manual
NER annotation. Use it to create an industry-leaning gold test set.

## Files

- `sample_texts.tsv`: source texts selected for manual annotation.
- `annotator_1.conll`: file for annotator 1.
- `annotator_2.conll`: file for annotator 2.
- `gold_resolved.conll`: created later by `src/resolve_gold.py`.

## Labels

Allowed BIO labels:

{chr(10).join(f"- `{label}`" for label in ALLOWED_LABELS)}

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
"""
    (output_dir / "README.md").write_text(content, encoding="utf-8")


def main() -> None:
    """Create the manual annotation package."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--sample-size", type=int, default=400)
    args = parser.parse_args()

    config = load_config(args.config)
    seed = int(config["training"]["seed"])
    corpus = read_corpus(Path(config["data"]["clean_file"]))
    sample_size = min(args.sample_size, len(corpus))
    sampled = random.Random(seed).sample(corpus, sample_size)

    args.output_dir.mkdir(parents=True, exist_ok=True)
    write_sample_texts(sampled, args.output_dir / "sample_texts.tsv")
    write_annotation_template(sampled, args.output_dir / "annotator_1.conll")
    write_annotation_template(sampled, args.output_dir / "annotator_2.conll")
    write_instructions(args.output_dir, sample_size)

    print(f"Prepared {sample_size} texts in {args.output_dir}")


if __name__ == "__main__":
    main()
