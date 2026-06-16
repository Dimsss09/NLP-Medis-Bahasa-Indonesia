"""Prepare manual review package for weak 11-label entities."""

from __future__ import annotations

import argparse
import csv
import json
import random
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from annotate_bio import Token, tokenize
from prepare_phase9_challenge_set import annotate_text, build_phrase_index, read_lines, read_sample_texts


DEFAULT_CORPUS = Path("data/clean/medical_text_corpus.txt")
DEFAULT_TRUE_GOLD = Path("data/true_gold_300/sample_texts.tsv")
DEFAULT_PHASE9 = Path("data/phase9_challenge_set/sample_texts.tsv")
DEFAULT_OUTPUT_DIR = Path("data/phase10_11label_manual_boost")

FOCUS_LABELS = ["RIWAYAT_PENYAKIT", "DOSIS", "PROSEDUR", "WAKTU_DURASI"]
FOCUS_PATTERNS = {
    "RIWAYAT_PENYAKIT": re.compile(r"\b(riwayat|pernah|penderita|menderita|memiliki riwayat)\b", re.IGNORECASE),
    "DOSIS": re.compile(
        r"\b(dosis|mg|mcg|gram|ml|cc|iu|unit|tablet|kapsul|sirup|sachet|tetes|salep|"
        r"sehari|kali sehari|2x|3x|1x|aturan pakai)\b",
        re.IGNORECASE,
    ),
    "PROSEDUR": re.compile(
        r"\b(operasi|caesar|kuretase|usg|rontgen|ct scan|mri|tes darah|cek darah|"
        r"testpack|pemeriksaan|vaksin|vaksinasi|divaksin|suntik|imunisasi|nebulizer)\b",
        re.IGNORECASE,
    ),
    "WAKTU_DURASI": re.compile(
        r"\b(hari|minggu|bulan|tahun|pagi|siang|malam|selama|sejak|"
        r"\d+\s*(hari|minggu|bulan|tahun)|[123]x)\b",
        re.IGNORECASE,
    ),
}


@dataclass(frozen=True)
class Candidate:
    source_id: str
    text: str
    focus_label: str
    focus_tags: tuple[str, ...]


def detect_tags(text: str) -> tuple[str, ...]:
    return tuple(label for label, pattern in FOCUS_PATTERNS.items() if pattern.search(text))


def select_candidates(corpus: list[str], excluded: set[str], per_label: int, seed: int) -> list[Candidate]:
    by_label: dict[str, list[Candidate]] = defaultdict(list)
    for line_number, text in enumerate(corpus, start=1):
        if text.casefold() in excluded:
            continue
        tags = detect_tags(text)
        for label in tags:
            by_label[label].append(Candidate(f"C{line_number:05d}", text, label, tags))

    rng = random.Random(seed)
    selected: list[Candidate] = []
    seen: set[str] = set()
    for label in FOCUS_LABELS:
        pool = by_label[label]
        rng.shuffle(pool)
        count = 0
        for candidate in pool:
            if candidate.text in seen:
                continue
            selected.append(candidate)
            seen.add(candidate.text)
            count += 1
            if count >= per_label:
                break
    selected.sort(key=lambda item: (FOCUS_LABELS.index(item.focus_label), item.source_id))
    return selected


def strengthen_weak_labels(tokens: list[Token], labels: list[str]) -> list[str]:
    """Add conservative draft labels for weak entities."""
    output = labels[:]
    lowered = [token.text.casefold() for token in tokens]

    for index, token in enumerate(lowered):
        if token in {"riwayat", "penderita"} and index + 1 < len(tokens):
            output[index] = "B-RIWAYAT_PENYAKIT"
            end = min(len(tokens), index + 5)
            for pos in range(index + 1, end):
                if lowered[pos] in {"dan", "dengan", "penyakit"} or output[pos].endswith(("-DIAGNOSIS", "-ALERGI")):
                    output[pos] = "I-RIWAYAT_PENYAKIT"
                elif pos == index + 1 and output[pos] != "O":
                    output[pos] = "I-RIWAYAT_PENYAKIT"
        if token in {"pernah", "menderita"} and index + 1 < len(tokens):
            output[index] = "O"
            if output[index + 1].endswith(("-DIAGNOSIS", "-ALERGI")):
                output[index + 1] = "B-RIWAYAT_PENYAKIT"
        if token in {"hari", "minggu", "bulan", "tahun", "pagi", "siang", "malam"}:
            if output[index] == "O":
                output[index] = "B-WAKTU_DURASI"
            if index > 0 and re.fullmatch(r"\d+", lowered[index - 1]) and output[index - 1] == "O":
                output[index - 1] = "B-WAKTU_DURASI"
                output[index] = "I-WAKTU_DURASI"
        if token in {"mg", "mcg", "gram", "ml", "cc", "tablet", "kapsul", "sirup", "sachet", "tetes", "salep"}:
            if index > 0 and re.fullmatch(r"\d+(?:[,.]\d+)?", lowered[index - 1]):
                output[index - 1] = "B-DOSIS"
                output[index] = "I-DOSIS"
            elif output[index] == "O":
                output[index] = "B-DOSIS"
    return output


def write_conll(candidates: list[Candidate], annotations: list[tuple[list[Token], list[str]]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as file:
        for candidate, (tokens, labels) in zip(candidates, annotations, strict=True):
            file.write(f"# id = {candidate.source_id}\n")
            file.write(f"# focus_label = {candidate.focus_label}\n")
            file.write(f"# focus_tags = {', '.join(candidate.focus_tags)}\n")
            file.write(f"# text = {candidate.text}\n")
            for token, label in zip(tokens, labels, strict=True):
                file.write(f"{token.text} {label}\n")
            file.write("\n")


def write_sample_texts(candidates: list[Candidate], path: Path) -> None:
    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file, delimiter="\t")
        writer.writerow(["id", "focus_label", "focus_tags", "text"])
        for candidate in candidates:
            writer.writerow([candidate.source_id, candidate.focus_label, ",".join(candidate.focus_tags), candidate.text])


def write_status(candidates: list[Candidate], path: Path) -> None:
    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file, delimiter="\t")
        writer.writerow(["id", "focus_label", "annotator_1_checked", "annotator_2_checked", "adjudicated", "notes"])
        for candidate in candidates:
            writer.writerow([candidate.source_id, candidate.focus_label, "no", "no", "no", ""])


def write_readme(output_dir: Path, candidates: list[Candidate], label_counts: Counter[str]) -> None:
    focus_counts = Counter(candidate.focus_label for candidate in candidates)
    focus_lines = "\n".join(f"- `{label}`: {focus_counts[label]}" for label in FOCUS_LABELS)
    label_lines = "\n".join(f"- `{label}`: {count}" for label, count in sorted(label_counts.items()))
    content = f"""# 11-Label Manual Boost Package

Generated at: {datetime.now(timezone.utc).isoformat()}

## Tujuan

Paket ini menambah contoh manual untuk 4 label yang masih lemah:
`RIWAYAT_PENYAKIT`, `DOSIS`, `PROSEDUR`, dan `WAKTU_DURASI`.

Label awal di file ini adalah draft otomatis. Dataset baru boleh disebut manual
gold setelah dua annotator manusia mengecek dan konflik diselesaikan manual.

## File

- `sample_texts.tsv`: daftar teks kandidat.
- `draft_labels.conll`: draft label awal.
- `annotator_1.conll`: file kerja annotator 1.
- `annotator_2.conll`: file kerja annotator 2.
- `human_review_status.tsv`: checklist progres review manusia.
- `MANUAL_REVIEW_GUIDE.md`: panduan singkat annotator.

## Jumlah contoh per fokus

{focus_lines}

## Ringkasan label draft

{label_lines}

## Setelah annotator selesai

```powershell
.\\venv\\Scripts\\python.exe src\\annotation_agreement.py --manual-dir data\\phase10_11label_manual_boost
```

Lalu isi konflik, kemudian:

```powershell
.\\venv\\Scripts\\python.exe src\\resolve_gold.py --manual-dir data\\phase10_11label_manual_boost
```
"""
    (output_dir / "README.md").write_text(content, encoding="utf-8")


def write_review_guide(output_dir: Path) -> None:
    content = """# Panduan Review Manual - 11 Label Boost

Pakai `docs/annotation_guidelines_11_label_journal_aligned.md` sebagai pegangan.

## Fokus Review

1. `RIWAYAT_PENYAKIT`
   - Tandai hanya bila jelas ada konteks riwayat.
   - Contoh: `riwayat TB`, `pernah menderita asma`.

2. `DOSIS`
   - Tandai angka+satuan, bentuk obat, frekuensi, dan aturan pakai.
   - Contoh: `500 mg`, `2 kali sehari`, `tablet`, `sirup`.

3. `PROSEDUR`
   - Tandai tindakan, pemeriksaan, vaksinasi, operasi, suntikan.
   - Contoh: `operasi caesar`, `pemeriksaan USG`, `vaksinasi covid`.

4. `WAKTU_DURASI`
   - Tandai ekspresi waktu/lama/frekuensi.
   - Contoh: `3 hari`, `2 minggu`, `pagi hari`, `tahun`.

## Jangan Lupa

- Jangan ubah token.
- Ubah label saja.
- Kalau draft salah, koreksi.
- Kalau ragu, catat di `human_review_status.tsv`.
"""
    (output_dir / "MANUAL_REVIEW_GUIDE.md").write_text(content, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--corpus", type=Path, default=DEFAULT_CORPUS)
    parser.add_argument("--true-gold", type=Path, default=DEFAULT_TRUE_GOLD)
    parser.add_argument("--phase9", type=Path, default=DEFAULT_PHASE9)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--per-label", type=int, default=50)
    parser.add_argument("--seed", type=int, default=110)
    args = parser.parse_args()

    excluded = read_sample_texts(args.true_gold) | read_sample_texts(args.phase9)
    candidates = select_candidates(read_lines(args.corpus), excluded, args.per_label, args.seed)
    phrase_index = build_phrase_index()
    annotations = []
    for candidate in candidates:
        tokens, labels = annotate_text(candidate.text, phrase_index)
        annotations.append((tokens, strengthen_weak_labels(tokens, labels)))

    args.output_dir.mkdir(parents=True, exist_ok=True)
    write_sample_texts(candidates, args.output_dir / "sample_texts.tsv")
    write_conll(candidates, annotations, args.output_dir / "draft_labels.conll")
    write_conll(candidates, annotations, args.output_dir / "annotator_1.conll")
    write_conll(candidates, annotations, args.output_dir / "annotator_2.conll")
    write_status(candidates, args.output_dir / "human_review_status.tsv")
    write_review_guide(args.output_dir)
    label_counts = Counter(label for _, labels in annotations for label in labels if label != "O")
    write_readme(args.output_dir, candidates, label_counts)
    manifest = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "dataset_type": "phase10_11label_manual_boost_draft",
        "human_gold": False,
        "human_review_required": True,
        "focus_labels": FOCUS_LABELS,
        "per_label_target": args.per_label,
        "sample_size": len(candidates),
        "label_counts": dict(label_counts),
        "files": {
            "sample_texts": str(args.output_dir / "sample_texts.tsv"),
            "draft_labels": str(args.output_dir / "draft_labels.conll"),
            "annotator_1": str(args.output_dir / "annotator_1.conll"),
            "annotator_2": str(args.output_dir / "annotator_2.conll"),
        },
    }
    (args.output_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Prepared {len(candidates)} examples in {args.output_dir}")


if __name__ == "__main__":
    main()
