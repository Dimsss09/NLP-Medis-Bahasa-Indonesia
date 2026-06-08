"""Integrated prediction pipeline for Indonesian medical NER, assertion status, and relation extraction."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.predict import load_model as load_ner_model, predict_entities


DEFAULT_NER_DIR = ROOT_DIR / "models" / "indobert-medical-ner-id"
DEFAULT_ASSERTION_DIR = ROOT_DIR / "models" / "indobert-medical-assertion-id"
DEFAULT_RELATION_DIR = ROOT_DIR / "models" / "indobert-medical-relation-id"

ASSERTION_LABELS = ["AFFIRMED", "NEGATED", "UNCERTAIN"]
RELATION_LABELS = ["no_relation", "dosage_of", "treats", "located_in"]


def run_hybrid_fallback(text: str, entities: list[dict], lexicon_path: Path) -> list[dict]:
    """Dynamically inject unmatched lexicon phrases and regex-based dosages."""
    import re
    import yaml

    # Load lexicon dynamically
    if lexicon_path.exists():
        with lexicon_path.open("r", encoding="utf-8") as file:
            lexicon = yaml.safe_load(file)
    else:
        lexicon = {}

    occupied_ranges = [(ent["start"], ent["end"]) for ent in entities]

    def is_overlap(start: int, end: int) -> bool:
        for o_start, o_end in occupied_ranges:
            if max(start, o_start) < min(end, o_end):
                return True
        return False

    new_entities = list(entities)
    entity_id_counter = len(entities) + 1

    # 1. Match lexicon phrases (longest first, globally sorted, case-insensitive, word boundary)
    global_phrases = []
    for label, phrases in lexicon.items():
        if isinstance(phrases, list):
            for phrase in phrases:
                global_phrases.append((phrase, label))
                
    global_phrases.sort(key=lambda x: len(x[0]), reverse=True)

    for phrase, label in global_phrases:
        escaped_phrase = re.escape(phrase.lower())
        pattern = re.compile(r'\b' + escaped_phrase + r'\b')
        
        for match in pattern.finditer(text.lower()):
            start, end = match.start(), match.end()
            if not is_overlap(start, end):
                new_entities.append({
                    "id": f"e{entity_id_counter}",
                    "text": text[start:end],
                    "label": label,
                    "start": start,
                    "end": end
                })
                occupied_ranges.append((start, end))
                entity_id_counter += 1

    # 2. Match regex dosage patterns (e.g. number + unit, frequencies, duration)
    dosage_units = r"(?:mg|mcg|g|gram|ml|cc|iu|tablet|kapsul|sendok|tetes|unit|puff|drops|ampul|vial|botol|keping|sachet|caps|tab|semprotan)"
    dosage_pattern1 = re.compile(r'\b\d+(?:[,.]\d+)?\s*' + dosage_units + r'\b', re.IGNORECASE)
    dosage_pattern2 = re.compile(r'\b\d+\s*[xX]\s*(?:sehari|hari|jam|minggu)?\b', re.IGNORECASE)
    # Pattern 3: verbal numbers e.g. 'tiga kali sehari', 'dua kali sehari'
    dosage_pattern3 = re.compile(r'\b(?:satu|dua|tiga|empat|lima|enam)\s+kali\s+(?:sehari|hari|jam|minggu)?\b', re.IGNORECASE)
    # Pattern 4: duration e.g. 'selama 5 hari', 'selama satu minggu'
    dosage_pattern4 = re.compile(r'\bselama\s+(?:\d+|satu|dua|tiga|empat|lima|enam)\s+(?:hari|minggu|bulan)\b', re.IGNORECASE)

    for pattern in [dosage_pattern1, dosage_pattern2, dosage_pattern3, dosage_pattern4]:
        for match in pattern.finditer(text):
            start, end = match.start(), match.end()
            if not is_overlap(start, end):
                new_entities.append({
                    "id": f"e{entity_id_counter}",
                    "text": text[start:end],
                    "label": "DOSIS",
                    "start": start,
                    "end": end
                })
                occupied_ranges.append((start, end))
                entity_id_counter += 1

    # Sort all entities by starting character offset
    new_entities.sort(key=lambda x: x["start"])
    
    # Re-assign sequential IDs e1, e2, ...
    for idx, ent in enumerate(new_entities):
        ent["id"] = f"e{idx+1}"

    return new_entities


def run_hybrid_relations(text: str, entities: list[dict], existing_relations: list[dict]) -> list[dict]:
    """Fallback rule-based relation extraction to handle high class imbalance."""
    relations = list(existing_relations)
    
    # Track existing pairs to avoid duplicates
    existing_pairs = {(r["head"], r["tail"]) for r in relations}
    
    # Tokenize text lowercased for token distances
    lowered_tokens = text.lower().split()
    
    # Map character start position to token index
    def get_token_index(char_start: int) -> int:
        return len(text[:char_start].split())
        
    # Inject token_start and token_end helper properties
    temp_entities = []
    for ent in entities:
        ent_copy = dict(ent)
        ent_copy["token_start"] = get_token_index(ent["start"])
        ent_copy["token_end"] = get_token_index(ent["end"])
        temp_entities.append(ent_copy)
        
    # Heuristic 1: dosage_of (DOSIS -> OBAT)
    dosages = [e for e in temp_entities if e["label"] == "DOSIS"]
    drugs = [e for e in temp_entities if e["label"] == "OBAT"]
    
    for dos in dosages:
        nearest_drug = None
        min_dist = 999
        for drug in drugs:
            dist = min(
                abs(dos["token_start"] - drug["token_end"]),
                abs(drug["token_start"] - dos["token_end"])
            )
            if dist < min_dist:
                min_dist = dist
                nearest_drug = drug
        if nearest_drug and min_dist <= 8:
            pair = (dos["id"], nearest_drug["id"])
            if pair not in existing_pairs:
                relations.append({
                    "head": dos["id"],
                    "tail": nearest_drug["id"],
                    "type": "dosage_of"
                })
                existing_pairs.add(pair)
                
    # Heuristic 2: treats (OBAT -> GEJALA/DIAGNOSIS)
    symptoms_diag = [e for e in temp_entities if e["label"] in {"GEJALA", "DIAGNOSIS"}]
    TREATS_LINKS = {"untuk", "obat", "meredakan", "mengobati", "atasi", "mengatasi", "sembuh", "penyembuh", "buat", "bagi", "reda"}
    
    for drug in drugs:
        for sd in symptoms_diag:
            dist = min(
                abs(drug["token_start"] - sd["token_end"]),
                abs(sd["token_start"] - drug["token_end"])
            )
            
            is_treats = False
            if dist <= 5:
                is_treats = True
            elif dist <= 10:
                # Check for linking words between entities
                start_search = min(drug["token_end"], sd["token_end"])
                end_search = max(drug["token_start"], sd["token_start"])
                middle_tokens = lowered_tokens[start_search:end_search]
                if any(t in TREATS_LINKS for t in middle_tokens):
                    is_treats = True
                    
            if is_treats:
                pair = (drug["id"], sd["id"])
                if pair not in existing_pairs:
                    relations.append({
                        "head": drug["id"],
                        "tail": sd["id"],
                        "type": "treats"
                    })
                    existing_pairs.add(pair)
                    
    # Heuristic 3: located_in (GEJALA/DIAGNOSIS -> ANATOMI)
    anatomy = [e for e in temp_entities if e["label"] == "ANATOMI"]
    for sd in symptoms_diag:
        for anat in anatomy:
            dist = min(
                abs(sd["token_start"] - anat["token_end"]),
                abs(anat["token_start"] - sd["token_end"])
            )
            if dist <= 6:
                pair = (sd["id"], anat["id"])
                if pair not in existing_pairs:
                    relations.append({
                        "head": sd["id"],
                        "tail": anat["id"],
                        "type": "located_in"
                    })
                    existing_pairs.add(pair)
                    
    return relations


class ClinicalPipeline:
    def __init__(self, ner_dir: Path, assertion_dir: Path, relation_dir: Path, device: str | None = None):
        # Device setup
        if device is None:
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        else:
            self.device = torch.device(device)
            
        print(f"Initializing Clinical Pipeline on device: {self.device}")
        
        # Load NER model
        self.ner_tok, self.ner_model, _ = load_ner_model(ner_dir, device=str(self.device))
        
        # Load Assertion model
        self.assert_tok = AutoTokenizer.from_pretrained(assertion_dir)
        self.assert_model = AutoModelForSequenceClassification.from_pretrained(assertion_dir)
        self.assert_model.to(self.device)
        self.assert_model.eval()
        
        # Load Relation model
        self.rel_tok = AutoTokenizer.from_pretrained(relation_dir)
        self.rel_model = AutoModelForSequenceClassification.from_pretrained(relation_dir)
        self.rel_model.to(self.device)
        self.rel_model.eval()

    def format_marked_text(self, text: str, head: dict, tail: dict) -> str:
        h_start, h_end = head["start"], head["end"]
        t_start, t_end = tail["start"], tail["end"]
        
        if h_start < t_start:
            return (
                text[:h_start]
                + "[START_HEAD] "
                + text[h_start:h_end]
                + " [END_HEAD]"
                + text[h_end:t_start]
                + "[START_TAIL] "
                + text[t_start:t_end]
                + " [END_TAIL]"
                + text[t_end:]
            )
        else:
            return (
                text[:t_start]
                + "[START_TAIL] "
                + text[t_start:t_end]
                + " [END_TAIL]"
                + text[t_end:h_start]
                + "[START_HEAD] "
                + text[h_start:h_end]
                + " [END_HEAD]"
                + text[h_end:]
            )

    def predict(self, text: str) -> dict:
        # 1. Run NER
        _, ner_spans = predict_entities(text, self.ner_tok, self.ner_model, self.device)
        
        entities = []
        for idx, span in enumerate(ner_spans):
            entities.append({
                "id": f"e{idx+1}",
                "text": span.text,
                "label": span.label,
                "start": span.start,
                "end": span.end
            })
            
        # Apply hybrid fallback matcher (Lexicon and Regex)
        lexicon_path = ROOT_DIR / "resources" / "medical_lexicon.yaml"
        entities = run_hybrid_fallback(text, entities, lexicon_path)
            
        # 2. Run Assertion Status Detection
        for ent in entities:
            if ent["label"] not in {"GEJALA", "DIAGNOSIS"}:
                continue
                
            start, end = ent["start"], ent["end"]
            marked_text = text[:start] + "[START_ENT] " + text[start:end] + " [END_ENT]" + text[end:]
            
            inputs = self.assert_tok(marked_text, return_tensors="pt", truncation=True, max_length=256)
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            with torch.no_grad():
                logits = self.assert_model(**inputs).logits
                pred_id = logits.argmax(dim=-1).item()
                ent["assertion"] = self.assert_model.config.id2label[pred_id]
                
        # 3. Run Relation Extraction
        relations = []
        candidates = []
        for e1 in entities:
            for e2 in entities:
                if e1["id"] == e2["id"]:
                    continue
                
                valid_pair = False
                if e1["label"] == "DOSIS" and e2["label"] == "OBAT":
                    valid_pair = True
                elif e1["label"] == "OBAT" and e2["label"] in {"GEJALA", "DIAGNOSIS"}:
                    valid_pair = True
                elif e1["label"] in {"GEJALA", "DIAGNOSIS"} and e2["label"] == "ANATOMI":
                    valid_pair = True
                    
                if valid_pair:
                    candidates.append((e1, e2))
                    
        for head, tail in candidates:
            marked_text = self.format_marked_text(text, head, tail)
            
            inputs = self.rel_tok(marked_text, return_tensors="pt", truncation=True, max_length=256)
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            with torch.no_grad():
                logits = self.rel_model(**inputs).logits.clone()
                
                # Apply type constraint masking on logits
                # RELATION_LABELS = ["no_relation", "dosage_of", "treats", "located_in"]
                allowed_indices = [0]  # "no_relation" is always allowed
                if head["label"] == "DOSIS" and tail["label"] == "OBAT":
                    allowed_indices.append(1)  # dosage_of
                elif head["label"] == "OBAT" and tail["label"] in {"GEJALA", "DIAGNOSIS"}:
                    allowed_indices.append(2)  # treats
                elif head["label"] in {"GEJALA", "DIAGNOSIS"} and tail["label"] == "ANATOMI":
                    allowed_indices.append(3)  # located_in
                
                # Set unallowed relation types to negative infinity
                for idx in range(logits.shape[-1]):
                    if idx not in allowed_indices:
                        logits[0, idx] = -1e9
                        
                pred_id = logits.argmax(dim=-1).item()
                rel_type = self.rel_model.config.id2label[pred_id]
                
                if rel_type != "no_relation":
                    relations.append({
                        "head": head["id"],
                        "tail": tail["id"],
                        "type": rel_type
                    })
                    
        # Apply hybrid fallback relation extraction
        relations = run_hybrid_relations(text, entities, relations)
                    
        return {
            "text": text,
            "entities": entities,
            "relations": relations
        }

    def add_to_graph(self, result: dict, kg_path: Path) -> None:
        """Add facts extracted from prediction into the global Knowledge Graph."""
        from src.knowledge_graph import MedicalKnowledgeGraph
        kg = MedicalKnowledgeGraph()
        kg.load_graph(kg_path)
        
        entities = result.get("entities", [])
        relations = result.get("relations", [])
        ent_map = {e["id"]: e for e in entities}
        
        for rel in relations:
            head_ent = ent_map.get(rel["head"])
            tail_ent = ent_map.get(rel["tail"])
            if head_ent and tail_ent:
                kg.add_fact(
                    head_name=head_ent["text"],
                    head_label=head_ent["label"],
                    relation=rel["type"],
                    tail_name=tail_ent["text"],
                    tail_label=tail_ent["label"]
                )
        kg.save_graph(kg_path)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("text", nargs="?", default="Pasien mengeluhkan demam tinggi dan sesak napas. Diberi paracetamol 500 mg untuk atasi demam, namun tidak batuk.")
    parser.add_argument("--ner-dir", type=Path, default=DEFAULT_NER_DIR)
    parser.add_argument("--assertion-dir", type=Path, default=DEFAULT_ASSERTION_DIR)
    parser.add_argument("--relation-dir", type=Path, default=DEFAULT_RELATION_DIR)
    args = parser.parse_args()
    
    pipeline = ClinicalPipeline(args.ner_dir, args.assertion_dir, args.relation_dir)
    result = pipeline.predict(args.text)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
