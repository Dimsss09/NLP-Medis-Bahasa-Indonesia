"""Build initial global Medical Knowledge Graph from relation training and validation data."""

from __future__ import annotations

import json
import argparse
from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.knowledge_graph import MedicalKnowledgeGraph


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--train-file", type=Path, default=Path("data/relations/train.json"))
    parser.add_argument("--val-file", type=Path, default=Path("data/relations/val.json"))
    parser.add_argument("--output-file", type=Path, default=Path("data/knowledge_graph.json"))
    args = parser.parse_args()

    kg = MedicalKnowledgeGraph()
    loaded_records = 0
    added_relations = 0

    # Process train and val splits
    for path in [args.train_file, args.val_file]:
        if not path.exists():
            print(f"Dataset file not found: {path}")
            continue
            
        print(f"Processing facts from: {path}")
        with path.open("r", encoding="utf-8") as file:
            records = json.load(file)
            
        for rec in records:
            loaded_records += 1
            entities = rec.get("entities", [])
            relations = rec.get("relations", [])
            
            # Map entity ID to entity dict
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
                    added_relations += 1

    # Save the populated graph
    kg.save_graph(args.output_file)
    
    print(f"Processed {loaded_records} sentences.")
    print(f"Extracted and merged {added_relations} relationships into global KG.")
    print(f"Knowledge Graph stats: {len(kg.graph.nodes)} nodes, {len(kg.graph.edges)} edges.")
    print(f"Saved global Knowledge Graph to {args.output_file}")


if __name__ == "__main__":
    main()
