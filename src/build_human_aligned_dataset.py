"""Build human-adjudication-aligned silver BIO data without using true-gold texts."""

from __future__ import annotations

import argparse
import json
import random
import re
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from annotate_bio import Token, tokenize, write_conll


DEFAULT_CORPUS = Path("data/clean/medical_text_corpus.txt")
DEFAULT_TRUE_GOLD_TEXTS = Path("data/true_gold_300/sample_texts.tsv")
DEFAULT_OUTPUT_DIR = Path("data/human_aligned_silver")

LABELS = ["GEJALA", "OBAT", "DOSIS", "DIAGNOSIS", "ANATOMI"]
SPLIT_RATIOS = {"train": 0.9, "val": 0.1}

ANATOMI = {
    "air mata",
    "area tangan",
    "badan",
    "bahu",
    "bibir",
    "bokong",
    "bulu kaki",
    "dada",
    "dahi",
    "gigi",
    "gusi",
    "hidung",
    "jantung",
    "jari",
    "jari tangan",
    "kaki",
    "kandungan",
    "kepala",
    "ketiak",
    "kulit",
    "kulit hidung",
    "kulit wajah",
    "lambung",
    "leher",
    "mata",
    "mata kanan",
    "mulut",
    "paha",
    "panggul",
    "paru",
    "payudara",
    "perut",
    "perut bawah",
    "pipi",
    "punggung",
    "puting",
    "puting payudara",
    "rahim",
    "saluran napas",
    "sela jari tangan",
    "sel telur",
    "siku",
    "tangan",
    "telapak tangan",
    "telinga",
    "tenggorokan",
    "tubuh",
    "vagina",
    "wajah",
}

GEJALA = {
    "badan lemas",
    "batuk",
    "batuk berdahak",
    "batuk berkepanjangan",
    "batuk kering",
    "belang",
    "belum haid",
    "belum kunjung haid",
    "belum pernah haid",
    "bengkak",
    "benjolan",
    "bentol",
    "bentolbentol",
    "berair",
    "bercak coklat",
    "berdarah",
    "berkepanjangan",
    "berwarna hitam",
    "biduran",
    "bintik",
    "bintik merah",
    "bruntusan",
    "cegukan",
    "darah haid",
    "darah menggumpal",
    "darah warna coklat",
    "demam",
    "demam tinggi",
    "diare",
    "flek coklat",
    "gatal",
    "gatalgatal",
    "gemetar",
    "haid sedikit",
    "hidung berdarah",
    "hidung tersumbat",
    "iritasi",
    "kaku",
    "keluar bercak coklat",
    "keluar cairan",
    "keluar darah",
    "keluar flek coklat",
    "kemerahan",
    "keputihan",
    "kram",
    "kulit merah",
    "lemas",
    "luka",
    "mata bengkak",
    "mata gatal",
    "mata perih",
    "mengi",
    "menstruasi tidak berhenti",
    "mual",
    "muntah",
    "nyeri",
    "oyong",
    "panas",
    "pandangan kabur",
    "pandangan gelap",
    "pegal",
    "pilek",
    "pusing",
    "rendahnya kadar hemoglobin",
    "ruam",
    "ruam gatal",
    "ruam merah",
    "sakit",
    "sakit gigi",
    "sakit kepala",
    "sakit perut",
    "sesak",
    "sesak napas",
    "siklus haid berubah",
    "siklus haid berubahubah",
    "siklus haid tidak lancar",
    "siklus haid tidak teratur",
    "siklus menstruasi tidak teratur",
    "telat haid",
    "telat menstruasi",
    "tenggorokan gatal",
    "tenggorokan sakit",
    "tersumbat",
    "tidak haid",
    "tidak kunjung sembuh",
    "tidak lancar",
    "tidak teratur",
}

DIAGNOSIS = {
    "alergi",
    "asam lambung",
    "asam urat",
    "asma",
    "asma bronkial",
    "biduran",
    "bisul",
    "breakout",
    "bronkitis",
    "copd",
    "dbd",
    "demam berdarah",
    "diabetes",
    "diabetes melitus",
    "eksim",
    "endometriosis",
    "flek paru",
    "floaters",
    "flu",
    "gangguan bipolar",
    "gastritis",
    "hamil",
    "herpes",
    "hipertensi",
    "hymen imperforata",
    "infeksi",
    "infeksi sekunder",
    "infeksi telinga",
    "infeksi trikomoniasis",
    "infark miokard akut",
    "iritasi",
    "jerawat",
    "keguguran",
    "kehamilan",
    "kolesterol tinggi",
    "maag",
    "miom",
    "panas dalam",
    "pco",
    "purging",
    "sinusitis",
    "stress",
    "tb",
    "tbc",
    "tipes",
    "trikomoniasis",
    "urtikaria",
    "uterus retrofleksi membesar",
}

OBAT = {
    "acyclovir",
    "air alkali",
    "aminofilin",
    "amoxicillin",
    "amoksisilin",
    "antibiotik",
    "asam mefenamat",
    "aspirin",
    "cetirizine",
    "coenzim q",
    "epsom salt",
    "exfoliating toner",
    "hand sanitizer",
    "handbody",
    "ibuprofen",
    "imunosupresan",
    "insulin",
    "jamu",
    "jamu pelancar haid",
    "jahe",
    "kafein",
    "kb",
    "kiranti",
    "krim",
    "krim perontok bulu",
    "larutan penyegar",
    "masker",
    "masker kopi",
    "masker lidah buaya",
    "masker sulfur",
    "methylprednisolone",
    "obat",
    "obat alergi",
    "obat asma",
    "obat batuk",
    "obat cacing",
    "obat flu",
    "obat herbal",
    "obat hormon",
    "obat imunosupresan",
    "obat jerawat",
    "obat kutu",
    "obat malaria",
    "obat nyeri",
    "obat penggemuk badan",
    "obat penambah nafsu makan",
    "obat penurun panas",
    "obat simvastatin",
    "obat tetes mata",
    "oralit",
    "paracetamol",
    "parasetamol",
    "pil kb",
    "produk perawatan kulit",
    "sabun wajah",
    "salbutamol",
    "salep",
    "salep mata",
    "simvastatin",
    "skincare",
    "softlens",
    "suntik kb",
    "suntik kontras",
    "suntik putih",
    "teh jati cina",
    "tenofovir",
    "teofilin",
    "vaksin covid",
    "vitamin",
    "vitamin c",
}

DOSIS_REGEXES = [
    re.compile(r"^\d+(?:[,.]\d+)?$"),
]
DOSIS_UNITS = {"mg", "mcg", "g", "gram", "ml", "cc", "iu", "unit"}
DOSIS_FORMS = {"sirup", "kapsul", "tablet", "tab", "sachet", "tetes", "semprotan", "salep"}
FREQ_WORDS = {"sehari", "hari", "minggu", "bulan", "pagi", "siang", "malam"}


@dataclass(frozen=True)
class Span:
    start: int
    end: int
    label: str


def phrase_tokens(phrase: str) -> tuple[str, ...]:
    return tuple(token.text.casefold() for token in tokenize(phrase))


def build_phrase_index() -> dict[str, list[tuple[str, ...]]]:
    raw = {
        "ANATOMI": ANATOMI,
        "DIAGNOSIS": DIAGNOSIS,
        "OBAT": OBAT,
        "GEJALA": GEJALA,
    }
    return {
        label: sorted({phrase_tokens(phrase) for phrase in phrases}, key=len, reverse=True)
        for label, phrases in raw.items()
    }


def find_phrase_spans(tokens: list[Token], phrases_by_label: dict[str, list[tuple[str, ...]]]) -> list[Span]:
    lowered = [token.text.casefold() for token in tokens]
    candidates: list[Span] = []
    # Anatomy first follows the adjudication rule that body parts stay separate.
    label_priority = {"ANATOMI": 0, "DIAGNOSIS": 1, "OBAT": 2, "GEJALA": 3}
    for label in ["ANATOMI", "DIAGNOSIS", "OBAT", "GEJALA"]:
        for phrase in phrases_by_label[label]:
            if not phrase:
                continue
            phrase_len = len(phrase)
            for start in range(0, len(tokens) - phrase_len + 1):
                end = start + phrase_len
                if tuple(lowered[start:end]) == phrase:
                    candidates.append(Span(start, end, label))

    candidates.sort(key=lambda span: (label_priority[span.label], -(span.end - span.start), span.start))
    occupied: set[int] = set()
    spans: list[Span] = []
    for span in candidates:
        if any(index in occupied for index in range(span.start, span.end)):
            continue
        spans.append(span)
        occupied.update(range(span.start, span.end))
    return spans


def add_dosage_spans(tokens: list[Token], spans: list[Span]) -> list[Span]:
    occupied = {index for span in spans for index in range(span.start, span.end)}
    lowered = [token.text.casefold() for token in tokens]
    new_spans = list(spans)
    index = 0
    while index < len(tokens):
        if index in occupied:
            index += 1
            continue
        token = lowered[index]
        next_token = lowered[index + 1] if index + 1 < len(tokens) else ""
        end = index
        if token in DOSIS_FORMS:
            end = index + 1
        elif any(regex.match(token) for regex in DOSIS_REGEXES) and next_token in DOSIS_UNITS:
            end = index + 2
        elif re.fullmatch(r"\d+x", token):
            end = index + 1
            while end < len(tokens) and lowered[end] in FREQ_WORDS:
                end += 1
        elif token.isdigit() and next_token in {"kali", "x"}:
            end = index + 2
            while end < len(tokens) and lowered[end] in FREQ_WORDS:
                end += 1

        if end > index and not any(pos in occupied for pos in range(index, end)):
            new_spans.append(Span(index, end, "DOSIS"))
            occupied.update(range(index, end))
            index = end
        else:
            index += 1
    return new_spans


def annotate_text(text: str, phrases_by_label: dict[str, list[tuple[str, ...]]]) -> tuple[list[Token], list[str]]:
    tokens = tokenize(text)
    labels = ["O"] * len(tokens)
    spans = add_dosage_spans(tokens, find_phrase_spans(tokens, phrases_by_label))
    for span in sorted(spans, key=lambda item: item.start):
        labels[span.start] = f"B-{span.label}"
        for index in range(span.start + 1, span.end):
            labels[index] = f"I-{span.label}"
    return tokens, labels


def read_lines(path: Path) -> list[str]:
    with path.open("r", encoding="utf-8") as file:
        return [line.strip() for line in file if line.strip()]


def read_true_gold_texts(path: Path) -> set[str]:
    texts: set[str] = set()
    if not path.exists():
        return texts
    with path.open("r", encoding="utf-8") as file:
        for line in file:
            if not line.strip():
                continue
            _, text = line.rstrip("\n").split("\t", 1)
            texts.add(text.casefold())
    return texts


def split_records(records: list[tuple[list[Token], list[str]]], seed: int) -> dict[str, list[tuple[list[Token], list[str]]]]:
    shuffled = records[:]
    random.Random(seed).shuffle(shuffled)
    train_end = int(len(shuffled) * SPLIT_RATIOS["train"])
    return {"train": shuffled[:train_end], "val": shuffled[train_end:]}


def count_entities(records: list[tuple[list[Token], list[str]]]) -> Counter[str]:
    counts: Counter[str] = Counter()
    for _, labels in records:
        for label in labels:
            if label.startswith("B-"):
                counts[label[2:]] += 1
    return counts


def write_manifest(output_dir: Path, records_total: int, excluded_total: int, splits: dict) -> None:
    manifest = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "dataset_type": "human_aligned_silver",
        "annotation_source": "rules_following_true_gold_adjudication_policy",
        "human_annotated": False,
        "human_gold": False,
        "true_gold_texts_excluded": excluded_total,
        "records_after_exclusion": records_total,
        "files": {
            "train": str(output_dir / "train.conll"),
            "validation": str(output_dir / "val.conll"),
        },
        "split_counts": {name: len(records) for name, records in splits.items()},
        "entity_counts": {name: dict(count_entities(records)) for name, records in splits.items()},
    }
    (output_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")


def write_report(output_dir: Path, records_total: int, excluded_total: int, splits: dict) -> None:
    lines = [
        "# Human-Aligned Silver Dataset",
        "",
        f"Generated at: {datetime.now(timezone.utc).isoformat()}",
        "",
        "## Status",
        "",
        "This dataset is automatically labeled, but the rules follow the",
        "`data/true_gold_300` adjudication policy. It is intended for retraining,",
        "not for final evaluation.",
        "",
        "The 300 texts from `data/true_gold_300/sample_texts.tsv` are excluded to",
        "keep the true gold benchmark held out.",
        "",
        "## Counts",
        "",
        f"- Excluded true-gold texts: {excluded_total}",
        f"- Records after exclusion: {records_total}",
        "",
        "## Split Counts",
        "",
        "| Split | Records | GEJALA | OBAT | DOSIS | DIAGNOSIS | ANATOMI |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for split_name, records in splits.items():
        counts = count_entities(records)
        lines.append(
            "| {split} | {records} | {gejala} | {obat} | {dosis} | {diagnosis} | {anatomi} |".format(
                split=split_name,
                records=len(records),
                gejala=counts["GEJALA"],
                obat=counts["OBAT"],
                dosis=counts["DOSIS"],
                diagnosis=counts["DIAGNOSIS"],
                anatomi=counts["ANATOMI"],
            )
        )
    (output_dir / "README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--corpus", type=Path, default=DEFAULT_CORPUS)
    parser.add_argument("--true-gold-texts", type=Path, default=DEFAULT_TRUE_GOLD_TEXTS)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    true_gold_texts = read_true_gold_texts(args.true_gold_texts)
    corpus = read_lines(args.corpus)
    filtered = [text for text in corpus if text.casefold() not in true_gold_texts]
    phrases_by_label = build_phrase_index()
    records = [annotate_text(text, phrases_by_label) for text in filtered]
    splits = split_records(records, args.seed)

    args.output_dir.mkdir(parents=True, exist_ok=True)
    write_conll(splits["train"], args.output_dir / "train.conll")
    write_conll(splits["val"], args.output_dir / "val.conll")
    write_manifest(args.output_dir, len(records), len(corpus) - len(filtered), splits)
    write_report(args.output_dir, len(records), len(corpus) - len(filtered), splits)
    print(
        "Wrote human-aligned silver splits: "
        f"train={len(splits['train'])}, val={len(splits['val'])}, "
        f"excluded_true_gold={len(corpus) - len(filtered)}"
    )


if __name__ == "__main__":
    main()
