"""Compute agreement between two manual CoNLL annotator files."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from sklearn.metrics import cohen_kappa_score
from seqeval.metrics import f1_score


DEFAULT_MANUAL_DIR = Path("data/manual_gold")
ALLOWED_LABELS = {
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
}


def read_conll(path: Path) -> list[tuple[list[str], list[str]]]:
    """Read CoNLL sentences while ignoring comment lines."""
    sentences: list[tuple[list[str], list[str]]] = []
    tokens: list[str] = []
    labels: list[str] = []
    with path.open("r", encoding="utf-8") as file:
        for raw_line in file:
            line = raw_line.strip()
            if line.startswith("#"):
                continue
            if not line:
                if tokens:
                    sentences.append((tokens, labels))
                    tokens = []
                    labels = []
                continue
            token, label = line.rsplit(" ", 1)
            tokens.append(token)
            labels.append(label)
    if tokens:
        sentences.append((tokens, labels))
    return sentences


def validate_pair(a: list[tuple[list[str], list[str]]], b: list[tuple[list[str], list[str]]]) -> list[str]:
    """Validate annotation files are structurally comparable."""
    errors: list[str] = []
    if len(a) != len(b):
        errors.append(f"sentence count mismatch: {len(a)} != {len(b)}")
        return errors
    for index, ((tokens_a, labels_a), (tokens_b, labels_b)) in enumerate(zip(a, b, strict=True), start=1):
        if tokens_a != tokens_b:
            errors.append(f"token mismatch in sentence {index}")
        invalid = [label for label in labels_a + labels_b if label not in ALLOWED_LABELS]
        if invalid:
            errors.append(f"invalid labels in sentence {index}: {sorted(set(invalid))}")
    return errors


def flatten(sentences: list[tuple[list[str], list[str]]]) -> list[str]:
    """Flatten labels."""
    return [label for _, labels in sentences for label in labels]


def is_incomplete(labels: list[str]) -> bool:
    """Detect untouched all-O annotation templates."""
    return bool(labels) and all(label == "O" for label in labels)


def write_conflicts(
    a: list[tuple[list[str], list[str]]],
    b: list[tuple[list[str], list[str]]],
    path: Path,
) -> int:
    """Write token-level conflicts for manual adjudication."""
    path.parent.mkdir(parents=True, exist_ok=True)
    conflict_count = 0
    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file, delimiter="\t")
        writer.writerow(["sentence_id", "token_id", "token", "annotator_1", "annotator_2", "resolved_label"])
        for sentence_id, ((tokens, labels_a), (_, labels_b)) in enumerate(zip(a, b, strict=True), start=1):
            for token_id, (token, label_a, label_b) in enumerate(zip(tokens, labels_a, labels_b, strict=True), start=1):
                if label_a != label_b:
                    conflict_count += 1
                    writer.writerow([sentence_id, token_id, token, label_a, label_b, ""])
    return conflict_count


def main() -> None:
    """Compute agreement and write conflict artifacts."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manual-dir", type=Path, default=DEFAULT_MANUAL_DIR)
    args = parser.parse_args()

    annotator_1 = read_conll(args.manual_dir / "annotator_1.conll")
    annotator_2 = read_conll(args.manual_dir / "annotator_2.conll")
    errors = validate_pair(annotator_1, annotator_2)
    labels_1 = flatten(annotator_1)
    labels_2 = flatten(annotator_2)
    incomplete = is_incomplete(labels_1) or is_incomplete(labels_2)
    conflict_count = 0 if errors else write_conflicts(annotator_1, annotator_2, args.manual_dir / "conflicts.tsv")

    cohen_kappa = 0.0 if incomplete or errors else cohen_kappa_score(labels_1, labels_2, labels=sorted(ALLOWED_LABELS))
    summary = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": "not_ready" if errors or incomplete else "ready_for_resolution",
        "errors": errors,
        "incomplete_template_detected": incomplete,
        "sentence_count": len(annotator_1),
        "token_count": len(labels_1),
        "token_agreement": sum(a == b for a, b in zip(labels_1, labels_2, strict=False)) / max(len(labels_1), 1),
        "cohen_kappa": cohen_kappa if labels_1 and labels_2 else 0.0,
        "entity_f1_between_annotators": f1_score(
            [labels for _, labels in annotator_1],
            [labels for _, labels in annotator_2],
            zero_division=0,
        )
        if not errors
        else 0.0,
        "conflict_count": conflict_count,
        "annotator_1_label_counts": dict(Counter(labels_1)),
        "annotator_2_label_counts": dict(Counter(labels_2)),
    }
    (args.manual_dir / "agreement_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    if summary["status"] != "ready_for_resolution":
        print("Manual annotations are not ready. See agreement_summary.json.")
        return
    print(f"Agreement ready. Conflicts: {conflict_count}")


if __name__ == "__main__":
    main()
