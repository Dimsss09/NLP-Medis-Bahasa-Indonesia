"""Build relation and assertion dataset from CoNLL NER files using heuristic rules."""

import argparse
import json
from pathlib import Path
import yaml


DEFAULT_CONFIG = Path("config.yaml")

NEGATION_CUES = {"tidak", "belum", "bukan", "tanpa", "jangan", "tidak ada", "bukanlah", "tiada"}
UNCERTAIN_CUES = {"mungkin", "kemungkinan", "curiga", "dicurigai", "gejala awal", "apakah", "sepertinya", "diduga", "indikasi"}
TREATS_LINKS = {"untuk", "obat", "meredakan", "mengobati", "atasi", "mengatasi", "sembuh", "penyembuh", "buat", "bagi", "reda"}


def read_conll_sentences(path: Path) -> list[list[tuple[str, str]]]:
    """Read CoNLL file and return a list of sentences, where each sentence is a list of (token, label) pairs."""
    sentences = []
    current_sentence = []
    with path.open("r", encoding="utf-8") as file:
        for raw_line in file:
            line = raw_line.strip()
            if not line:
                if current_sentence:
                    sentences.append(current_sentence)
                    current_sentence = []
                continue
            if line.startswith("#"):
                continue
            token, label = line.rsplit(" ", 1)
            current_sentence.append((token, label))
    if current_sentence:
        sentences.append(current_sentence)
    return sentences


def extract_entities(sentence_tokens: list[tuple[str, str]]) -> list[dict]:
    """Extract BIO entities from a sentence and return list of entity dicts with offsets."""
    entities = []
    current_entity = None
    
    # Reconstruct text and map token index to character start/end
    text_parts = []
    token_chars = [] # list of (start, end)
    current_char = 0
    
    for token, _ in sentence_tokens:
        start = current_char
        end = start + len(token)
        token_chars.append((start, end))
        text_parts.append(token)
        current_char = end + 1 # assume 1 space between tokens
        
    full_text = " ".join(text_parts)
    
    # BIO entity extraction
    for idx, (token, label) in enumerate(sentence_tokens):
        if label.startswith("B-"):
            if current_entity:
                entities.append(current_entity)
            entity_type = label[2:]
            current_entity = {
                "id": f"e{len(entities) + 1}",
                "text": token,
                "label": entity_type,
                "token_start": idx,
                "token_end": idx + 1,
                "start": token_chars[idx][0],
                "end": token_chars[idx][1]
            }
        elif label.startswith("I-"):
            entity_type = label[2:]
            if current_entity and current_entity["label"] == entity_type:
                current_entity["token_end"] = idx + 1
                current_entity["end"] = token_chars[idx][1]
                current_entity["text"] = full_text[current_entity["start"]:current_entity["end"]]
            else:
                # Fallback if I- starts without B-
                if current_entity:
                    entities.append(current_entity)
                current_entity = {
                    "id": f"e{len(entities) + 1}",
                    "text": token,
                    "label": entity_type,
                    "token_start": idx,
                    "token_end": idx + 1,
                    "start": token_chars[idx][0],
                    "end": token_chars[idx][1]
                }
        else: # "O"
            if current_entity:
                entities.append(current_entity)
                current_entity = None
                
    if current_entity:
        entities.append(current_entity)
        
    return full_text, entities


def annotate_assertion(full_text: str, entities: list[dict], sentence_tokens: list[tuple[str, str]]) -> list[dict]:
    """Annotate assertion status (NEGATED, UNCERTAIN, AFFIRMED) for Symptoms & Diagnosis."""
    lowered_tokens = [t[0].lower() for t in sentence_tokens]
    
    for ent in entities:
        if ent["label"] not in {"GEJALA", "DIAGNOSIS"}:
            continue
            
        start_token = ent["token_start"]
        
        # Check window before the entity (up to 4 tokens)
        lookback = max(0, start_token - 4)
        context_tokens = lowered_tokens[lookback:start_token]
        
        assertion = "AFFIRMED"
        
        # Check for multi-word cues first
        context_str = " ".join(context_tokens)
        if "tidak ada" in context_str or "bebas dari" in context_str:
            assertion = "NEGATED"
        elif "gejala awal" in context_str or "diduga kuat" in context_str:
            assertion = "UNCERTAIN"
        else:
            # Check single word cues
            for tok in context_tokens:
                if tok in NEGATION_CUES:
                    assertion = "NEGATED"
                    break
                elif tok in UNCERTAIN_CUES:
                    assertion = "UNCERTAIN"
                    break
                    
        # Check trailing tokens for negation e.g. "absen", "negatif"
        if assertion == "AFFIRMED" and ent["token_end"] < len(lowered_tokens):
            next_tok = lowered_tokens[ent["token_end"]]
            if next_tok in {"negatif", "absen", "nihil"}:
                assertion = "NEGATED"
                
        ent["assertion"] = assertion
        
    return entities


def annotate_relations(entities: list[dict], sentence_tokens: list[tuple[str, str]]) -> list[dict]:
    """Extract relation triples between entities in a sentence based on proximity and labels."""
    relations = []
    lowered_tokens = [t[0].lower() for t in sentence_tokens]
    
    # dosage_of: DOSIS -> OBAT
    dosages = [e for e in entities if e["label"] == "DOSIS"]
    drugs = [e for e in entities if e["label"] == "OBAT"]
    
    for dos in dosages:
        # Find nearest drug
        nearest_drug = None
        min_dist = 999
        for drug in drugs:
            dist = min(abs(dos["token_start"] - drug["token_end"]), abs(drug["token_start"] - dos["token_end"]))
            if dist < min_dist:
                min_dist = dist
                nearest_drug = drug
        if nearest_drug and min_dist <= 8:
            relations.append({
                "head": dos["id"],
                "tail": nearest_drug["id"],
                "type": "dosage_of"
            })
            
    # treats: OBAT -> GEJALA / DIAGNOSIS
    symptoms_diag = [e for e in entities if e["label"] in {"GEJALA", "DIAGNOSIS"}]
    for drug in drugs:
        for sd in symptoms_diag:
            dist = min(abs(drug["token_start"] - sd["token_end"]), abs(sd["token_start"] - drug["token_end"]))
            if dist <= 5:
                relations.append({
                    "head": drug["id"],
                    "tail": sd["id"],
                    "type": "treats"
                })
            elif dist <= 10:
                # Check for linking words
                start_search = min(drug["token_end"], sd["token_end"])
                end_search = max(drug["token_start"], sd["token_start"])
                middle_tokens = lowered_tokens[start_search:end_search]
                if any(t in TREATS_LINKS for t in middle_tokens):
                    relations.append({
                        "head": drug["id"],
                        "tail": sd["id"],
                        "type": "treats"
                    })
                    
    # located_in: GEJALA / DIAGNOSIS -> ANATOMI
    anatomy = [e for e in entities if e["label"] == "ANATOMI"]
    for sd in symptoms_diag:
        for anat in anatomy:
            dist = min(abs(sd["token_start"] - anat["token_end"]), abs(anat["token_start"] - sd["token_end"]))
            if dist <= 6:
                relations.append({
                    "head": sd["id"],
                    "tail": anat["id"],
                    "type": "located_in"
                })
                
    return relations


def process_conll_file(conll_path: Path, output_path: Path) -> int:
    """Read a CoNLL file, annotate relations and assertions, and save as JSON."""
    sentences = read_conll_sentences(conll_path)
    output_records = []
    
    for sentence_tokens in sentences:
        if not sentence_tokens:
            continue
        full_text, entities = extract_entities(sentence_tokens)
        entities = annotate_assertion(full_text, entities, sentence_tokens)
        relations = annotate_relations(entities, sentence_tokens)
        
        # Clean internal helper offsets before output
        cleaned_entities = []
        for ent in entities:
            cleaned_ent = {
                "id": ent["id"],
                "text": ent["text"],
                "label": ent["label"],
                "start": ent["start"],
                "end": ent["end"]
            }
            if "assertion" in ent:
                cleaned_ent["assertion"] = ent["assertion"]
            cleaned_entities.append(cleaned_ent)
            
        output_records.append({
            "text": full_text,
            "entities": cleaned_entities,
            "relations": relations
        })
        
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as file:
        json.dump(output_records, file, indent=2, ensure_ascii=False)
        
    return len(output_records)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    args = parser.parse_args()
    
    with args.config.open("r", encoding="utf-8") as file:
        config = yaml.safe_load(file)
        
    data_config = config["data"]
    train_config = config.get("training", {})
    train_source = train_config.get("train_data_source", "annotated")
    
    if train_source == "silver":
        train_conll = Path(data_config["silver_train_file"])
        val_conll = Path(data_config["silver_validation_file"])
        test_conll = Path(data_config["silver_test_file"])
        print("Using SILVER CoNLL files for relation dataset generation.")
    else:
        train_conll = Path(data_config["train_file"])
        val_conll = Path(data_config["validation_file"])
        test_conll = Path(data_config["test_file"])
        print("Using ANNOTATED CoNLL files for relation dataset generation.")
        
    splits = {
        "train": (train_conll, Path("data/relations/train.json")),
        "val": (val_conll, Path("data/relations/val.json")),
        "test": (test_conll, Path("data/relations/test.json"))
    }
    
    for split_name, (conll_path, json_path) in splits.items():
        if not conll_path.exists():
            print(f"CoNLL file not found: {conll_path}")
            continue
        count = process_conll_file(conll_path, json_path)
        print(f"Processed {count} sentences for {split_name} split -> saved to {json_path}")


if __name__ == "__main__":
    main()
