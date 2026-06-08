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
                logits = self.rel_model(**inputs).logits
                pred_id = logits.argmax(dim=-1).item()
                rel_type = self.rel_model.config.id2label[pred_id]
                
                if rel_type != "no_relation":
                    relations.append({
                        "head": head["id"],
                        "tail": tail["id"],
                        "type": rel_type
                    })
                    
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
