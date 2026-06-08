"""Prediction helpers for Indonesian medical NER."""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path

import torch
from transformers import AutoModelForTokenClassification, AutoTokenizer


DEFAULT_MODEL_DIR = Path("models/indobert-medical-ner-id")


@dataclass(frozen=True)
class EntitySpan:
    """A predicted entity span."""

    text: str
    label: str
    start: int
    end: int


@dataclass(frozen=True)
class TokenPrediction:
    """Token-level prediction with character offsets."""

    token: str
    label: str
    start: int
    end: int


def load_model(model_dir: Path | str = DEFAULT_MODEL_DIR, device: str | None = None):
    """Load tokenizer, model, and device for inference."""
    model_dir = Path(model_dir)
    tokenizer = AutoTokenizer.from_pretrained(model_dir)
    model = AutoModelForTokenClassification.from_pretrained(model_dir)
    if device is None:
        device = "cuda" if torch.cuda.is_available() else "cpu"
    device_obj = torch.device(device)
    model.to(device_obj)
    model.eval()
    return tokenizer, model, device_obj


def predict_tokens(text: str, tokenizer, model, device: torch.device) -> list[TokenPrediction]:
    """Predict BIO labels and project subword predictions back to words."""
    encoded = tokenizer(
        text,
        return_offsets_mapping=True,
        return_tensors="pt",
        truncation=True,
        max_length=256,
    )
    offsets = encoded.pop("offset_mapping")[0].tolist()
    word_ids = encoded.word_ids(batch_index=0)
    encoded = {key: value.to(device) for key, value in encoded.items()}

    with torch.no_grad():
        logits = model(**encoded).logits
        prediction_ids = logits.argmax(dim=-1)[0].cpu().tolist()

    predictions: list[TokenPrediction] = []
    seen_words: set[int] = set()
    for token_index, (token_id, word_id) in enumerate(zip(prediction_ids, word_ids, strict=True)):
        if word_id is None or word_id in seen_words:
            continue
        word_offsets = [
            offset
            for offset, candidate_word_id in zip(offsets, word_ids, strict=True)
            if candidate_word_id == word_id and offset[0] != offset[1]
        ]
        if not word_offsets:
            continue
        start = min(offset[0] for offset in word_offsets)
        end = max(offset[1] for offset in word_offsets)
        token_text = text[start:end]
        label = model.config.id2label[int(token_id)]
        predictions.append(TokenPrediction(token=token_text, label=label, start=start, end=end))
        seen_words.add(word_id)
    return predictions


def merge_wordpiece_predictions(predictions: list[TokenPrediction]) -> list[TokenPrediction]:
    """Merge subword predictions that share a contiguous entity label."""
    merged: list[TokenPrediction] = []
    for prediction in predictions:
        if not merged:
            merged.append(prediction)
            continue

        previous = merged[-1]
        same_label = prediction.label == previous.label and prediction.label != "O"
        touching = prediction.start <= previous.end + 1
        if same_label and touching:
            merged[-1] = TokenPrediction(
                token=f"{previous.token}{prediction.token}",
                label=previous.label,
                start=previous.start,
                end=prediction.end,
            )
        else:
            merged.append(prediction)
    return merged


def extract_entities(text: str, predictions: list[TokenPrediction]) -> list[EntitySpan]:
    """Convert BIO token predictions into entity spans."""
    entities: list[EntitySpan] = []
    current_label: str | None = None
    current_start: int | None = None
    current_end: int | None = None

    for prediction in predictions:
        label = prediction.label
        if label == "O":
            if current_label is not None and current_start is not None and current_end is not None:
                entities.append(EntitySpan(text=text[current_start:current_end], label=current_label, start=current_start, end=current_end))
            current_label = None
            current_start = None
            current_end = None
            continue

        prefix, entity_label = label.split("-", 1)
        starts_new = prefix == "B" or current_label != entity_label
        if starts_new:
            if current_label is not None and current_start is not None and current_end is not None:
                entities.append(EntitySpan(text=text[current_start:current_end], label=current_label, start=current_start, end=current_end))
            current_label = entity_label
            current_start = prediction.start
            current_end = prediction.end
        else:
            current_end = prediction.end

    if current_label is not None and current_start is not None and current_end is not None:
        entities.append(EntitySpan(text=text[current_start:current_end], label=current_label, start=current_start, end=current_end))
    return entities


def predict_entities(text: str, tokenizer, model, device: torch.device) -> tuple[list[TokenPrediction], list[EntitySpan]]:
    """Predict token labels and merged entity spans."""
    token_predictions = merge_wordpiece_predictions(predict_tokens(text, tokenizer, model, device))
    entities = extract_entities(text, token_predictions)
    return token_predictions, entities


def main() -> None:
    """CLI prediction entry point."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("text", nargs="?", default="Pasien demam dan minum paracetamol 500 mg.")
    parser.add_argument("--model-dir", type=Path, default=DEFAULT_MODEL_DIR)
    args = parser.parse_args()

    tokenizer, model, device = load_model(args.model_dir)
    token_predictions, entities = predict_entities(args.text, tokenizer, model, device)
    payload = {
        "tokens": [prediction.__dict__ for prediction in token_predictions],
        "entities": [entity.__dict__ for entity in entities],
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
