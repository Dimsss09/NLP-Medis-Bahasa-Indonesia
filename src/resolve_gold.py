"""Resolve two annotator files into a gold CoNLL file after adjudication."""

from __future__ import annotations

import argparse
import csv
import json
from datetime import datetime, timezone
from pathlib import Path

from annotation_agreement import ALLOWED_LABELS, flatten, is_incomplete, read_conll, validate_pair


DEFAULT_MANUAL_DIR = Path("data/manual_gold")


def load_resolutions(path: Path) -> dict[tuple[int, int], str]:
    """Load resolved labels from conflicts.tsv."""
    resolutions: dict[tuple[int, int], str] = {}
    if not path.exists():
        return resolutions
    with path.open("r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file, delimiter="\t")
        for row in reader:
            label = row.get("resolved_label", "").strip()
            if not label:
                continue
            if label not in ALLOWED_LABELS:
                raise ValueError(f"Invalid resolved label: {label}")
            resolutions[(int(row["sentence_id"]), int(row["token_id"]))] = label
    return resolutions


def main() -> None:
    """Create gold_resolved.conll if all conflicts are adjudicated."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manual-dir", type=Path, default=DEFAULT_MANUAL_DIR)
    args = parser.parse_args()

    annotator_1 = read_conll(args.manual_dir / "annotator_1.conll")
    annotator_2 = read_conll(args.manual_dir / "annotator_2.conll")
    errors = validate_pair(annotator_1, annotator_2)
    if errors:
        raise SystemExit("; ".join(errors))
    if is_incomplete(flatten(annotator_1)) or is_incomplete(flatten(annotator_2)):
        raise SystemExit("Manual annotator files still look like untouched all-O templates.")

    resolutions = load_resolutions(args.manual_dir / "conflicts.tsv")
    unresolved: list[dict[str, int | str]] = []
    output_path = args.manual_dir / "gold_resolved.conll"
    with output_path.open("w", encoding="utf-8", newline="\n") as file:
        for sentence_id, ((tokens, labels_a), (_, labels_b)) in enumerate(zip(annotator_1, annotator_2, strict=True), start=1):
            for token_id, (token, label_a, label_b) in enumerate(zip(tokens, labels_a, labels_b, strict=True), start=1):
                if label_a == label_b:
                    label = label_a
                else:
                    key = (sentence_id, token_id)
                    label = resolutions.get(key)
                    if label is None:
                        unresolved.append({"sentence_id": sentence_id, "token_id": token_id, "token": token})
                        label = label_a
                file.write(f"{token} {label}\n")
            file.write("\n")

    summary = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": "blocked_unresolved_conflicts" if unresolved else "gold_ready",
        "unresolved_conflicts": unresolved,
        "gold_file": str(output_path),
    }
    (args.manual_dir / "gold_resolution_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    if unresolved:
        raise SystemExit(f"Gold set still has {len(unresolved)} unresolved conflicts.")
    print(f"Gold set written to {output_path}")


if __name__ == "__main__":
    main()
