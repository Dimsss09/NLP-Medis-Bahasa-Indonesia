"""Simulate manual annotations from two independent annotators with random disagreements."""

import argparse
import random
from pathlib import Path
import yaml

from annotate_bio import load_lexicon, tokenize, annotate_tokens, load_yaml


DEFAULT_CONFIG = Path("config.yaml")
DEFAULT_LEXICON = Path("resources/medical_lexicon.yaml")
ALLOWED_LABELS = ["GEJALA", "OBAT", "DOSIS", "DIAGNOSIS", "ANATOMI"]


def get_entities_from_labels(labels: list[str]) -> list[tuple[int, int, str]]:
    """Extract entities with their start/end index and label type from BIO labels."""
    entities = []
    current_entity = None  # (start, type)
    
    for i, label in enumerate(labels):
        if label.startswith("B-"):
            if current_entity:
                entities.append((current_entity[0], i, current_entity[1]))
            current_entity = (i, label[2:])
        elif label.startswith("I-"):
            if current_entity and label[2:] != current_entity[1]:
                # Label mismatch, close previous and start new or ignore
                entities.append((current_entity[0], i, current_entity[1]))
                current_entity = None
        else: # "O"
            if current_entity:
                entities.append((current_entity[0], i, current_entity[1]))
                current_entity = None
                
    if current_entity:
        entities.append((current_entity[0], len(labels), current_entity[1]))
        
    return entities


def apply_noise_to_labels(labels: list[str], seed: int) -> list[str]:
    """Simulate human annotation noise by randomly modifying entities."""
    rng = random.Random(seed)
    new_labels = labels[:]
    entities = get_entities_from_labels(labels)
    
    for start, end, label_type in entities:
        rand_val = rng.random()
        if rand_val < 0.06:
            # Missed detection: change all to "O"
            for i in range(start, end):
                new_labels[i] = "O"
        elif rand_val < 0.10:
            # Label confusion: change to another random entity type
            other_types = [t for t in ALLOWED_LABELS if t != label_type]
            new_type = rng.choice(other_types)
            new_labels[start] = f"B-{new_type}"
            for i in range(start + 1, end):
                new_labels[i] = f"I-{new_type}"
                
    return new_labels


def read_sample_texts(path: Path) -> list[str]:
    """Read sampled source texts from TSV."""
    texts = []
    with path.open("r", encoding="utf-8") as file:
        for line in file:
            if not line.strip():
                continue
            _, text = line.strip().split("\t", 1)
            texts.append(text)
    return texts


def write_conll(texts: list[str], labels_list: list[list[str]], path: Path) -> None:
    """Write token-label pairs in CoNLL format."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as file:
        for text, labels in zip(texts, labels_list):
            file.write(f"# text = {text}\n")
            tokens = tokenize(text)
            for token, label in zip(tokens, labels, strict=True):
                file.write(f"{token.text} {label}\n")
            file.write("\n")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--lexicon", type=Path, default=DEFAULT_LEXICON)
    args = parser.parse_args()
    
    config = load_yaml(args.config)
    data_config = config["data"]
    manual_gold_dir = Path(data_config["manual_gold_dir"])
    
    # Load texts and lexicon
    texts = read_sample_texts(manual_gold_dir / "sample_texts.tsv")
    lexicon = load_lexicon(args.lexicon)
    
    # Generate base annotations (lexicon rules)
    base_annotations = []
    for text in texts:
        tokens = tokenize(text)
        labels = annotate_tokens(tokens, lexicon)
        base_annotations.append(labels)
        
    # Annotator 1: Use base annotations
    annotator_1_labels = base_annotations
    
    # Annotator 2: Apply random disagreements
    annotator_2_labels = []
    for idx, labels in enumerate(base_annotations):
        # Seed based on index to ensure deterministic run
        annotator_2_labels.append(apply_noise_to_labels(labels, seed=42 + idx))
        
    # Write files
    write_conll(texts, annotator_1_labels, manual_gold_dir / "annotator_1.conll")
    write_conll(texts, annotator_2_labels, manual_gold_dir / "annotator_2.conll")
    
    print(f"Simulated annotations written to {manual_gold_dir}")


if __name__ == "__main__":
    main()
