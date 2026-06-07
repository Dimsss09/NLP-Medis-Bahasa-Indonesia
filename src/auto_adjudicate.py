"""Automatically resolve conflicts in conflicts.tsv by choosing annotator_1 labels."""

from pathlib import Path
import csv


DEFAULT_MANUAL_DIR = Path("data/manual_gold")


def main() -> None:
    conflicts_path = DEFAULT_MANUAL_DIR / "conflicts.tsv"
    if not conflicts_path.exists():
        print("No conflicts.tsv found.")
        return
        
    rows = []
    with conflicts_path.open("r", encoding="utf-8", newline="") as file:
        reader = csv.reader(file, delimiter="\t")
        header = next(reader)
        
        # Determine column indexes
        annotator_1_idx = header.index("annotator_1")
        resolved_label_idx = header.index("resolved_label")
        
        for row in reader:
            # Resolve conflict by choosing annotator_1's label
            row[resolved_label_idx] = row[annotator_1_idx]
            rows.append(row)
            
    with conflicts_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file, delimiter="\t")
        writer.writerow(header)
        writer.writerows(rows)
        
    print(f"Automatically resolved {len(rows)} conflicts in {conflicts_path}")


if __name__ == "__main__":
    main()
