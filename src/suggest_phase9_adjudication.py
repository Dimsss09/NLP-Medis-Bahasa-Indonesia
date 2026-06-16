"""Create suggested adjudication labels for Phase 9 conflicts.

Suggestions are only a review aid. Do not treat them as human adjudication until
a human reviewer accepts or edits the `resolved_label` values.
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


DEFAULT_CONFLICTS = Path("data/phase9_challenge_set/conflicts.tsv")
DEFAULT_OUTPUT = Path("data/phase9_challenge_set/conflicts_suggested.tsv")

TEMPORAL_CONNECTORS = {"setelah", "pasca", "saat", "usai"}
SYMPTOM_CONNECTORS = {"terasa", "muncul", "timbul", "keluar", "sering", "selalu"}
PROCEDURE_HINTS = {"testpack", "tes", "cek", "pemeriksaan", "vaksin", "vaksinasi", "operasi", "suntik", "usg", "rontgen", "mri"}
LAB_VALUE_HINTS = {"tinggi", "rendah", "rendahnya", "normal", "negatif", "positif", "peningkatan", "meningkat", "menurun"}
RIWAYAT_HINTS = {"riwayat", "pernah"}


def label_type(label: str) -> str:
    if label == "O":
        return "O"
    return label.split("-", 1)[1]


def label_prefix(label: str) -> str:
    if label == "O":
        return "O"
    return label.split("-", 1)[0]


def choose_bio_boundary(token_id: int, desired_type: str, conflict_rows: list[dict[str, str]]) -> str:
    if token_id <= 1:
        return f"B-{desired_type}"
    previous_conflict = next(
        (row for row in conflict_rows if int(row["token_id"]) == token_id - 1),
        None,
    )
    if previous_conflict is not None:
        previous_labels = {
            previous_conflict["annotator_1"],
            previous_conflict["annotator_2"],
            previous_conflict.get("suggested_label", ""),
        }
        if any(label.endswith(f"-{desired_type}") for label in previous_labels):
            return f"I-{desired_type}"
    return f"B-{desired_type}"


def suggest(row: dict[str, str], sentence_rows: list[dict[str, str]]) -> tuple[str, str]:
    token = row["token"].casefold()
    label_1 = row["annotator_1"]
    label_2 = row["annotator_2"]
    type_1 = label_type(label_1)
    type_2 = label_type(label_2)

    if type_1 == type_2 and type_1 != "O":
        if label_prefix(label_1) == label_prefix(label_2):
            return label_1, "annotator sama tipe dan boundary sama"
        token_id = int(row["token_id"])
        if "B-" in {label_1[:2], label_2[:2]}:
            return f"B-{type_1}", "beda B/I pada tipe sama; pilih B agar aman dari I tanpa awal span"
        return choose_bio_boundary(token_id, type_1, sentence_rows), "beda B/I pada tipe sama; saran boundary BIO"

    non_o_labels = [label for label in (label_1, label_2) if label != "O"]
    if len(non_o_labels) == 1:
        chosen = non_o_labels[0]
        chosen_type = label_type(chosen)
        if chosen_type == "WAKTU_DURASI" and token in TEMPORAL_CONNECTORS:
            return "O", "kata penghubung waktu; label WAKTU_DURASI hanya jika benar-benar waktu/durasi"
        if chosen_type == "GEJALA" and token in SYMPTOM_CONNECTORS:
            return "O", "kata kerja/penghubung gejala; sesuai aturan adjudikasi lama"
        if chosen_type == "PROSEDUR" and token in PROCEDURE_HINTS:
            return chosen, "token kuat sebagai prosedur/pemeriksaan"
        if chosen_type == "NILAI_LAB" and token in LAB_VALUE_HINTS:
            return chosen, "token kuat sebagai nilai hasil"
        if chosen_type == "RIWAYAT_PENYAKIT" and token in RIWAYAT_HINTS:
            return chosen, "token kuat sebagai riwayat"
        return chosen, "satu annotator memberi entitas; perlu cek cepat"

    if {"OBAT", "PROSEDUR"} == {type_1, type_2} and token in {"kb", "suntik", "vaksin", "imunisasi"}:
        token_id = int(row["token_id"])
        return choose_bio_boundary(token_id, "PROSEDUR", sentence_rows), "suntik/vaksin/kb lebih cocok sebagai prosedur pada fase 9"

    if {"HASIL_LAB", "NILAI_LAB"} & {type_1, type_2}:
        return label_1, "konflik lab; pakai saran annotator 1 sebagai awal, tetap review manual"

    return "", "ambigu; wajib diputuskan manual"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--conflicts", type=Path, default=DEFAULT_CONFLICTS)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    with args.conflicts.open("r", encoding="utf-8", newline="") as file:
        rows = list(csv.DictReader(file, delimiter="\t"))

    rows_by_sentence: dict[str, list[dict[str, str]]] = {}
    for row in rows:
        rows_by_sentence.setdefault(row["sentence_id"], []).append(row)

    for sentence_rows in rows_by_sentence.values():
        sentence_rows.sort(key=lambda item: int(item["token_id"]))
        for row in sentence_rows:
            suggested_label, note = suggest(row, sentence_rows)
            row["suggested_label"] = suggested_label
            row["suggestion_note"] = note
            if not row.get("resolved_label"):
                row["resolved_label"] = suggested_label

    fieldnames = list(rows[0].keys()) if rows else []
    for field in ["suggested_label", "suggestion_note"]:
        if field not in fieldnames:
            fieldnames.append(field)

    with args.output.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, delimiter="\t", fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    filled = sum(1 for row in rows if row.get("resolved_label"))
    print(f"Wrote {args.output} with {filled}/{len(rows)} suggested resolutions.")


if __name__ == "__main__":
    main()
