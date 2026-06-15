"""Prepare Phase 9 challenge-set annotation package.

The generated labels are AI/rule drafts only. They are meant to reduce manual
work, not to replace human review.
"""

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
from build_human_aligned_dataset import ANATOMI, DIAGNOSIS, DOSIS_FORMS, GEJALA, OBAT


DEFAULT_CORPUS = Path("data/clean/medical_text_corpus.txt")
DEFAULT_TRUE_GOLD_TEXTS = Path("data/true_gold_300/sample_texts.tsv")
DEFAULT_OUTPUT_DIR = Path("data/phase9_challenge_set")

ENTITY_TYPES = [
    "GEJALA",
    "OBAT",
    "DOSIS",
    "DIAGNOSIS",
    "ANATOMI",
    "PROSEDUR",
    "HASIL_LAB",
    "NILAI_LAB",
    "WAKTU_DURASI",
    "ALERGI",
    "RIWAYAT_PENYAKIT",
]

FOCUS_REGEXES = {
    "ALERGI": re.compile(r"\b(alergi|hipersensitivitas|reaksi)\b", re.IGNORECASE),
    "PROSEDUR": re.compile(
        r"\b(operasi|caesar|ct scan|rontgen|usg|mri|tes darah|cek darah|pemeriksaan|suntik|vaksin|vaksinasi|imunisasi|radiologi|medical check up)\b",
        re.IGNORECASE,
    ),
    "HASIL_LAB": re.compile(
        r"\b(lab|leukosit|hemoglobin|hb|gula darah|kolesterol|asam urat|trombosit|eosinofil|eritrosit|urin|urine)\b",
        re.IGNORECASE,
    ),
    "WAKTU_DURASI": re.compile(r"\b(hari|minggu|bulan|tahun|pagi|siang|malam|sejak|selama|pasca|setelah|usai)\b", re.IGNORECASE),
    "RIWAYAT_PENYAKIT": re.compile(r"\b(riwayat|pernah|memiliki riwayat)\b", re.IGNORECASE),
    "OBAT_DOSIS": re.compile(r"\b(obat|dosis|mg|ml|tablet|kapsul|sirup|salep|tetes|cetirizine|paracetamol|amoxicillin)\b", re.IGNORECASE),
    "GEJALA_SULIT": re.compile(r"\b(gatal|nyeri|bengkak|ruam|sesak|batuk|mual|pusing|bentol|perih|demam)\b", re.IGNORECASE),
}

EXTRA_PHRASES = {
    "ALERGI": {
        "alergi",
        "alergi debu",
        "alergi dingin",
        "alergi kulit",
        "alergi kosmetik",
        "alergi makanan",
        "alergi protein",
        "alergi susu",
        "hipersensitivitas",
        "reaksi alergi",
    },
    "PROSEDUR": {
        "cek darah",
        "ct scan",
        "foto rontgen",
        "foto thorax",
        "imunisasi",
        "medical check up",
        "mri",
        "operasi",
        "operasi caesar",
        "operasi katarak",
        "operasi kista",
        "operasi usus buntu",
        "pemeriksaan",
        "pemeriksaan darah",
        "pemeriksaan dokter",
        "pemeriksaan foto thorax",
        "pemeriksaan lab",
        "pemeriksaan radiologi",
        "rontgen",
        "suntik",
        "suntik kb",
        "suntik kontras",
        "suntik putih",
        "tes darah",
        "tes lab",
        "usg",
        "vaksin",
        "vaksin covid",
        "vaksinasi covid",
    },
    "HASIL_LAB": {
        "asam urat",
        "eosinofil",
        "eritrosit",
        "gula darah",
        "hb",
        "hemoglobin",
        "hasil lab",
        "hasil pemeriksaan darah",
        "kolesterol",
        "kadar eritrosit",
        "kadar hemoglobin",
        "kadar leukosit",
        "leukosit",
        "pemeriksaan lab darah",
        "tes darah",
        "trombosit",
        "urin",
        "urine",
    },
    "NILAI_LAB": {
        "normal",
        "rendah",
        "rendahnya",
        "tinggi",
        "peningkatan",
        "meningkat",
        "menurun",
    },
    "WAKTU_DURASI": {
        "hari",
        "minggu",
        "bulan",
        "tahun",
        "pagi hari",
        "malam hari",
        "setelah",
        "sejak",
        "selama",
        "pasca",
        "usai",
    },
    "RIWAYAT_PENYAKIT": {
        "riwayat alergi",
        "riwayat alergi debu",
        "riwayat hipersensitivitas",
        "riwayat sinusitis",
        "riwayat suntik alergi",
        "riwayat tb",
    },
}

BASE_PHRASES = {
    "ANATOMI": ANATOMI,
    "DIAGNOSIS": DIAGNOSIS - {"alergi"},
    "OBAT": OBAT,
    "GEJALA": GEJALA - {"alergi", "biduran"},
}

LABEL_PRIORITY = [
    "RIWAYAT_PENYAKIT",
    "PROSEDUR",
    "HASIL_LAB",
    "NILAI_LAB",
    "WAKTU_DURASI",
    "ALERGI",
    "ANATOMI",
    "DIAGNOSIS",
    "OBAT",
    "GEJALA",
]


@dataclass(frozen=True)
class Candidate:
    source_id: str
    text: str
    focus_tags: tuple[str, ...]


@dataclass(frozen=True)
class Span:
    start: int
    end: int
    label: str


def read_lines(path: Path) -> list[str]:
    with path.open("r", encoding="utf-8") as file:
        return [line.strip() for line in file if line.strip()]


def read_sample_texts(path: Path) -> set[str]:
    if not path.exists():
        return set()
    texts: set[str] = set()
    with path.open("r", encoding="utf-8") as file:
        for raw_line in file:
            line = raw_line.strip()
            if not line:
                continue
            parts = line.split("\t")
            text = parts[-1]
            if text.lower() != "text":
                texts.add(text.casefold())
    return texts


def detect_focus_tags(text: str) -> tuple[str, ...]:
    tags = [name for name, pattern in FOCUS_REGEXES.items() if pattern.search(text)]
    return tuple(tags)


def select_candidates(corpus: list[str], excluded: set[str], sample_size: int, seed: int) -> list[Candidate]:
    by_tag: dict[str, list[Candidate]] = defaultdict(list)
    all_candidates: list[Candidate] = []
    for line_number, text in enumerate(corpus, start=1):
        if text.casefold() in excluded:
            continue
        tags = detect_focus_tags(text)
        if not tags:
            continue
        candidate = Candidate(source_id=f"C{line_number:05d}", text=text, focus_tags=tags)
        all_candidates.append(candidate)
        for tag in tags:
            by_tag[tag].append(candidate)

    rng = random.Random(seed)
    for candidates in by_tag.values():
        rng.shuffle(candidates)

    selected: list[Candidate] = []
    seen: set[str] = set()
    tag_order = ["HASIL_LAB", "PROSEDUR", "RIWAYAT_PENYAKIT", "OBAT_DOSIS", "GEJALA_SULIT", "ALERGI", "WAKTU_DURASI"]
    quota = max(10, sample_size // len(tag_order))
    for tag in tag_order:
        for candidate in by_tag.get(tag, [])[:quota]:
            if candidate.text not in seen:
                selected.append(candidate)
                seen.add(candidate.text)
            if len(selected) >= sample_size:
                return selected

    all_candidates.sort(key=lambda item: (-len(item.focus_tags), item.source_id))
    for candidate in all_candidates:
        if candidate.text not in seen:
            selected.append(candidate)
            seen.add(candidate.text)
        if len(selected) >= sample_size:
            break
    return selected


def phrase_tokens(phrase: str) -> tuple[str, ...]:
    return tuple(token.text.casefold() for token in tokenize(phrase))


def build_phrase_index() -> dict[str, list[tuple[str, ...]]]:
    phrases = {label: set(values) for label, values in BASE_PHRASES.items()}
    for label, values in EXTRA_PHRASES.items():
        phrases.setdefault(label, set()).update(values)
    return {
        label: sorted({phrase_tokens(phrase) for phrase in values}, key=len, reverse=True)
        for label, values in phrases.items()
    }


def find_phrase_spans(tokens: list[Token], phrase_index: dict[str, list[tuple[str, ...]]]) -> list[Span]:
    lowered = [token.text.casefold() for token in tokens]
    candidates: list[Span] = []
    priority = {label: index for index, label in enumerate(LABEL_PRIORITY)}
    for label in LABEL_PRIORITY:
        for phrase in phrase_index.get(label, []):
            phrase_len = len(phrase)
            for start in range(0, len(tokens) - phrase_len + 1):
                end = start + phrase_len
                if tuple(lowered[start:end]) == phrase:
                    candidates.append(Span(start, end, label))

    candidates.sort(key=lambda span: (priority[span.label], -(span.end - span.start), span.start))
    occupied: set[int] = set()
    spans: list[Span] = []
    for span in candidates:
        if any(index in occupied for index in range(span.start, span.end)):
            continue
        spans.append(span)
        occupied.update(range(span.start, span.end))
    return spans


def add_dosis_spans(tokens: list[Token], spans: list[Span]) -> list[Span]:
    occupied = {index for span in spans for index in range(span.start, span.end)}
    lowered = [token.text.casefold() for token in tokens]
    new_spans = list(spans)
    for index, token in enumerate(lowered):
        if index in occupied:
            continue
        next_token = lowered[index + 1] if index + 1 < len(tokens) else ""
        end = index
        if token in DOSIS_FORMS:
            end = index + 1
        elif re.fullmatch(r"\d+(?:[,.]\d+)?", token) and next_token in {"mg", "mcg", "g", "gram", "ml", "cc", "iu", "unit"}:
            end = index + 2
        elif re.fullmatch(r"\d+x", token):
            end = index + 1
        if end > index and not any(pos in occupied for pos in range(index, end)):
            new_spans.append(Span(index, end, "DOSIS"))
            occupied.update(range(index, end))
    return new_spans


def add_lab_value_spans(tokens: list[Token], spans: list[Span]) -> list[Span]:
    occupied = {index for span in spans for index in range(span.start, span.end)}
    lab_positions = {index for span in spans if span.label == "HASIL_LAB" for index in range(span.start, span.end)}
    if not lab_positions:
        return spans
    lowered = [token.text.casefold() for token in tokens]
    value_words = {"tinggi", "rendah", "rendahnya", "normal", "peningkatan", "meningkat", "menurun"}
    new_spans = list(spans)
    for index, token in enumerate(lowered):
        if index in occupied or token not in value_words:
            continue
        if any(abs(index - lab_index) <= 4 for lab_index in lab_positions):
            new_spans.append(Span(index, index + 1, "NILAI_LAB"))
            occupied.add(index)
    return new_spans


def annotate_text(text: str, phrase_index: dict[str, list[tuple[str, ...]]]) -> tuple[list[Token], list[str]]:
    tokens = tokenize(text)
    labels = ["O"] * len(tokens)
    spans = add_lab_value_spans(tokens, add_dosis_spans(tokens, find_phrase_spans(tokens, phrase_index)))
    for span in sorted(spans, key=lambda item: item.start):
        labels[span.start] = f"B-{span.label}"
        for index in range(span.start + 1, span.end):
            labels[index] = f"I-{span.label}"
    return tokens, labels


def write_conll(candidates: list[Candidate], annotations: list[tuple[list[Token], list[str]]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as file:
        for candidate, (tokens, labels) in zip(candidates, annotations, strict=True):
            file.write(f"# id = {candidate.source_id}\n")
            file.write(f"# focus = {', '.join(candidate.focus_tags)}\n")
            file.write(f"# text = {candidate.text}\n")
            for token, label in zip(tokens, labels, strict=True):
                file.write(f"{token.text} {label}\n")
            file.write("\n")


def write_sample_texts(candidates: list[Candidate], path: Path) -> None:
    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file, delimiter="\t")
        writer.writerow(["id", "focus_tags", "text"])
        for candidate in candidates:
            writer.writerow([candidate.source_id, ",".join(candidate.focus_tags), candidate.text])


def write_review_status(candidates: list[Candidate], path: Path) -> None:
    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file, delimiter="\t")
        writer.writerow(["id", "annotator_1_checked", "annotator_2_checked", "adjudicated", "notes"])
        for candidate in candidates:
            writer.writerow([candidate.source_id, "no", "no", "no", ""])


def write_labels(path: Path) -> None:
    labels = ["O"] + [f"{prefix}-{entity}" for entity in ENTITY_TYPES for prefix in ("B", "I")]
    path.write_text("\n".join(labels) + "\n", encoding="utf-8")


def write_readme(output_dir: Path, sample_size: int, focus_counts: Counter[str], label_counts: Counter[str]) -> None:
    focus_lines = "\n".join(f"- `{label}`: {count}" for label, count in sorted(focus_counts.items()))
    label_lines = "\n".join(f"- `{label}`: {count}" for label, count in sorted(label_counts.items()))
    content = f"""# Phase 9 Challenge Set

Generated at: {datetime.now(timezone.utc).isoformat()}

## Tujuan

Folder ini berisi {sample_size} kandidat teks untuk memperkuat benchmark proyek.
Fokusnya adalah kasus yang lebih sulit: dosis, obat, gejala, alergi, prosedur,
hasil lab, nilai lab, waktu/durasi, dan riwayat penyakit.

## Status penting

File ini belum boleh disebut gold dataset. Label awal dibuat otomatis sebagai
draft bantuan. Dataset baru boleh disebut manual/gold setelah manusia mengecek
labelnya dan konflik diselesaikan manual.

## File

- `sample_texts.tsv`: daftar teks yang dipilih.
- `draft_labels.conll`: label awal dari aturan/AI, hanya untuk bantuan review.
- `annotator_1.conll`: salinan draft untuk dikoreksi annotator 1.
- `annotator_2.conll`: salinan draft untuk dikoreksi annotator 2.
- `labels.txt`: daftar label yang boleh dipakai.
- `human_review_status.tsv`: checklist sederhana agar tahu mana yang sudah dicek.
- `adjudication_notes.md`: tempat mencatat keputusan konflik.

## Cara kerja

1. Annotator 1 membuka `annotator_1.conll` dan mengoreksi label yang salah.
2. Annotator 2 membuka `annotator_2.conll` dan mengoreksi label secara terpisah.
3. Tandai progres di `human_review_status.tsv`.
4. Jalankan agreement:

```powershell
.\\venv\\Scripts\\python.exe src\\annotation_agreement.py --manual-dir data\\phase9_challenge_set
```

5. Isi `conflicts.tsv` pada kolom `resolved_label`.
6. Jalankan resolve:

```powershell
.\\venv\\Scripts\\python.exe src\\resolve_gold.py --manual-dir data\\phase9_challenge_set
```

## Ringkasan fokus teks

{focus_lines}

## Ringkasan label draft

{label_lines}

## Aturan tambahan label baru

- `ALERGI`: kondisi alergi atau jenis alerginya, misalnya alergi debu.
- `PROSEDUR`: tindakan atau pemeriksaan, misalnya operasi caesar, rontgen, USG, vaksin.
- `HASIL_LAB`: nama pemeriksaan/parameter lab, misalnya leukosit, hemoglobin, gula darah.
- `NILAI_LAB`: nilai atau status hasil lab, misalnya tinggi, rendah, normal.
- `WAKTU_DURASI`: waktu atau lama keluhan, misalnya hari, minggu, bulan, pagi hari.
- `RIWAYAT_PENYAKIT`: riwayat kondisi sebelumnya, misalnya riwayat TB atau riwayat alergi.
"""
    (output_dir / "README.md").write_text(content, encoding="utf-8")


def write_adjudication_notes(path: Path) -> None:
    content = """# Adjudication Notes - Phase 9

Isi file ini saat menyelesaikan konflik annotator.

## Keputusan yang perlu dicatat

- Apakah `alergi` dipakai sebagai `ALERGI` atau tetap `DIAGNOSIS` pada konteks tertentu?
- Apakah `vaksin` dianggap `PROSEDUR` atau `OBAT`?
- Apakah kata waktu seperti `tahun` pada usia pasien tetap `WAKTU_DURASI` atau `O`?
- Apakah `kolesterol tinggi` menjadi `DIAGNOSIS`, atau `HASIL_LAB` + `NILAI_LAB`?

## Catatan keputusan final

- 
"""
    path.write_text(content, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--corpus", type=Path, default=DEFAULT_CORPUS)
    parser.add_argument("--true-gold-texts", type=Path, default=DEFAULT_TRUE_GOLD_TEXTS)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--sample-size", type=int, default=160)
    parser.add_argument("--seed", type=int, default=49)
    args = parser.parse_args()

    corpus = read_lines(args.corpus)
    excluded = read_sample_texts(args.true_gold_texts)
    candidates = select_candidates(corpus, excluded, args.sample_size, args.seed)
    phrase_index = build_phrase_index()
    annotations = [annotate_text(candidate.text, phrase_index) for candidate in candidates]

    args.output_dir.mkdir(parents=True, exist_ok=True)
    write_sample_texts(candidates, args.output_dir / "sample_texts.tsv")
    write_conll(candidates, annotations, args.output_dir / "draft_labels.conll")
    write_conll(candidates, annotations, args.output_dir / "annotator_1.conll")
    write_conll(candidates, annotations, args.output_dir / "annotator_2.conll")
    write_labels(args.output_dir / "labels.txt")
    write_review_status(candidates, args.output_dir / "human_review_status.tsv")
    write_adjudication_notes(args.output_dir / "adjudication_notes.md")

    focus_counts = Counter(tag for candidate in candidates for tag in candidate.focus_tags)
    label_counts = Counter(label for _, labels in annotations for label in labels if label != "O")
    write_readme(args.output_dir, len(candidates), focus_counts, label_counts)
    manifest = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "dataset_type": "phase9_challenge_set_draft",
        "human_gold": False,
        "human_review_required": True,
        "sample_size": len(candidates),
        "excluded_true_gold_texts": len(excluded),
        "focus_counts": dict(focus_counts),
        "draft_label_counts": dict(label_counts),
        "files": {
            "sample_texts": str(args.output_dir / "sample_texts.tsv"),
            "draft_labels": str(args.output_dir / "draft_labels.conll"),
            "annotator_1": str(args.output_dir / "annotator_1.conll"),
            "annotator_2": str(args.output_dir / "annotator_2.conll"),
        },
    }
    (args.output_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Prepared Phase 9 challenge set: {len(candidates)} texts in {args.output_dir}")


if __name__ == "__main__":
    main()
