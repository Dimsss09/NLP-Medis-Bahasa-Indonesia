"""Generate a compact model error analysis from Phase 4 artifacts."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path


DEFAULT_METRICS = Path("reports/evaluation_metrics.json")
DEFAULT_CONFUSION = Path("reports/evaluation_confusion_matrix.csv")
DEFAULT_EXAMPLES = Path("reports/evaluation_prediction_examples.jsonl")
DEFAULT_OUTPUT = Path("reports/error_analysis.md")


def load_confusions(path: Path) -> list[tuple[str, str, int]]:
    """Load non-diagonal confusion matrix entries."""
    rows: list[tuple[str, str, int]] = []
    with path.open("r", encoding="utf-8", newline="") as file:
        reader = csv.reader(file)
        header = next(reader)
        predicted_labels = header[1:]
        for row in reader:
            gold = row[0]
            for predicted, count_text in zip(predicted_labels, row[1:], strict=True):
                count = int(count_text)
                if gold != predicted and count > 0:
                    rows.append((gold, predicted, count))
    return sorted(rows, key=lambda item: item[2], reverse=True)


def load_examples(path: Path) -> list[dict]:
    """Load prediction examples."""
    examples: list[dict] = []
    with path.open("r", encoding="utf-8") as file:
        for line in file:
            if line.strip():
                examples.append(json.loads(line))
    return examples


def main() -> None:
    """Write error analysis report."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--metrics", type=Path, default=DEFAULT_METRICS)
    parser.add_argument("--confusion", type=Path, default=DEFAULT_CONFUSION)
    parser.add_argument("--examples", type=Path, default=DEFAULT_EXAMPLES)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    metrics = json.loads(args.metrics.read_text(encoding="utf-8"))
    confusions = load_confusions(args.confusion)
    examples = load_examples(args.examples)
    incorrect_examples = [example for example in examples if example["status"] == "incorrect"]
    predicted_counts = Counter(metrics.get("predicted_label_counts", {}))

    lines = [
        "# Error Analysis",
        "",
        "## Summary",
        "",
        f"- Micro F1: {metrics['micro_f1']:.4f}",
        f"- Token accuracy: {metrics['token_accuracy']:.4f}",
        f"- Sentence exact match: {metrics['sentence_exact_match']:.4f}",
        "",
        "## Main Failure Modes",
        "",
    ]

    if predicted_counts.get("B-DOSIS", 0) == 0:
        lines.append("- The model did not predict any `B-DOSIS` labels, so dosage recall is zero.")
    obat_recall = metrics["seqeval_report"].get("OBAT", {}).get("recall", 0.0)
    if obat_recall < 0.8:
        lines.append("- `OBAT` is under-predicted; recall is low despite high precision.")
    elif predicted_counts.get("B-OBAT", 0) < metrics["gold_label_counts"].get("B-OBAT", 0):
        lines.append("- `OBAT` still has a small number of missed mentions despite high overall recall.")
    lines.append("- The model is biased toward labels seen often in the bootstrap training subset.")
    lines.append("- Metrics are still measured against semi-automatic labels, not a human gold set.")

    lines.extend(["", "## Largest Token-Level Confusions", "", "| Gold | Predicted | Count |", "| --- | --- | ---: |"])
    for gold, predicted, count in confusions[:10]:
        lines.append(f"| {gold} | {predicted} | {count} |")

    lines.extend(["", "## Example Incorrect Predictions", ""])
    for example in incorrect_examples[:5]:
        lines.append(f"- Text: {' '.join(example['tokens'])}")
        lines.append(f"  Gold: {' '.join(example['gold_labels'])}")
        lines.append(f"  Pred: {' '.join(example['predicted_labels'])}")

    lines.extend(
        [
            "",
            "## Recommended Fixes",
            "",
            "- Complete manual double annotation and evaluate on `gold_resolved.conll`.",
            "- Add more manually validated `DOSIS` and `OBAT` examples to training.",
            "- Train on a larger subset or full training set when GPU time is available.",
            "- Review ambiguous lexicon labels before reporting final performance.",
        ]
    )
    args.output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {args.output}")


if __name__ == "__main__":
    main()
