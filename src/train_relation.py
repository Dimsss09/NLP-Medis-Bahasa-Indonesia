"""Train a relation classifier using IndoBERT."""

import argparse
import json
import random
from pathlib import Path
import numpy as np
import torch
from torch.utils.data import DataLoader, Dataset
from tqdm.auto import tqdm
from transformers import AutoTokenizer, AutoModelForSequenceClassification, get_linear_schedule_with_warmup


DEFAULT_CONFIG = Path("config.yaml")
DEFAULT_MODEL_NAME = "indobenchmark/indobert-base-p1"
DEFAULT_OUTPUT_DIR = Path("models/indobert-medical-relation-id")

RELATION_MAP = {"no_relation": 0, "dosage_of": 1, "treats": 2, "located_in": 3}
INV_RELATION_MAP = {v: k for k, v in RELATION_MAP.items()}


def set_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


class RelationDataset(Dataset):
    def __init__(self, encodings, labels):
        self.encodings = encodings
        self.labels = labels

    def __getitem__(self, idx):
        item = {key: torch.tensor(val[idx]) for key, val in self.encodings.items()}
        item["labels"] = torch.tensor(self.labels[idx], dtype=torch.long)
        return item

    def __len__(self):
        return len(self.labels)


def format_marked_text(text: str, head: dict, tail: dict) -> str:
    """Insert head and tail entity markers into the text based on their positions."""
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


def load_relation_samples(json_path: Path) -> list[dict]:
    """Generate positive and negative relation samples from JSON dataset."""
    samples = []
    with json_path.open("r", encoding="utf-8") as file:
        records = json.load(file)
        
    for rec in records:
        text = rec["text"]
        entities = rec["entities"]
        relations = rec["relations"]
        
        # Build lookup for positive relations
        pos_relations = {}
        for rel in relations:
            pos_relations[(rel["head"], rel["tail"])] = rel["type"]
            
        # Group entities by ID
        ent_by_id = {ent["id"]: ent for ent in entities}
        
        # Generate candidate pairs
        # Rule: Only pair DOSIS -> OBAT, OBAT -> GEJALA/DIAGNOSIS, GEJALA/DIAGNOSIS -> ANATOMI
        candidates = []
        
        for e1 in entities:
            for e2 in entities:
                if e1["id"] == e2["id"]:
                    continue
                
                # Check valid candidate pairings
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
            # Check if this pair is a positive relation
            rel_type = pos_relations.get((head["id"], tail["id"]), "no_relation")
            label_id = RELATION_MAP[rel_type]
            
            # Format text
            marked_text = format_marked_text(text, head, tail)
            samples.append({
                "text": marked_text,
                "label": label_id
            })
            
    return samples


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--train-file", type=Path, default=Path("data/relations/train.json"))
    parser.add_argument("--val-file", type=Path, default=Path("data/relations/val.json"))
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--epochs", type=int, default=3)
    parser.add_argument("--batch-size", type=int, default=16)
    parser.add_argument("--lr", type=float, default=2e-5)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    
    set_seed(args.seed)
    
    # Load samples
    train_samples = load_relation_samples(args.train_file)
    val_samples = load_relation_samples(args.val_file)
    print(f"Loaded {len(train_samples)} training relation samples, {len(val_samples)} validation samples")
    
    # Check class distribution
    train_labels = [s["label"] for s in train_samples]
    dist = {k: train_labels.count(v) for k, v in RELATION_MAP.items()}
    print(f"Train class distribution: {dist}")
    
    # Initialize tokenizer and model
    tokenizer = AutoTokenizer.from_pretrained(DEFAULT_MODEL_NAME)
    # Add special tokens
    special_tokens = {
        "additional_special_tokens": ["[START_HEAD]", "[END_HEAD]", "[START_TAIL]", "[END_TAIL]"]
    }
    tokenizer.add_special_tokens(special_tokens)
    
    model = AutoModelForSequenceClassification.from_pretrained(DEFAULT_MODEL_NAME, num_labels=4)
    model.resize_token_embeddings(len(tokenizer))
    
    # Set labels in config
    model.config.id2label = INV_RELATION_MAP
    model.config.label2id = RELATION_MAP
    
    # Tokenize
    train_texts = [s["text"] for s in train_samples]
    val_texts = [s["text"] for s in val_samples]
    val_labels = [s["label"] for s in val_samples]
    
    train_encodings = tokenizer(train_texts, truncation=True, padding=True, max_length=256)
    val_encodings = tokenizer(val_texts, truncation=True, padding=True, max_length=256)
    
    train_dataset = RelationDataset(train_encodings, train_labels)
    val_dataset = RelationDataset(val_encodings, val_labels)
    
    train_loader = DataLoader(train_dataset, batch_size=args.batch_size, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=args.batch_size, shuffle=False)
    
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)
    print(f"Training on device: {device}")
    
    optimizer = torch.optim.AdamW(model.parameters(), lr=args.lr, weight_decay=0.01)
    total_steps = len(train_loader) * args.epochs
    scheduler = get_linear_schedule_with_warmup(
        optimizer,
        num_warmup_steps=int(total_steps * 0.1),
        num_training_steps=total_steps
    )
    
    for epoch in range(args.epochs):
        model.train()
        total_loss = 0.0
        progress = tqdm(train_loader, desc=f"Epoch {epoch + 1}/{args.epochs}")
        for batch in progress:
            batch = {k: v.to(device) for k, v in batch.items()}
            outputs = model(**batch)
            loss = outputs.loss
            loss.backward()
            
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()
            scheduler.step()
            optimizer.zero_grad()
            
            total_loss += loss.item()
            progress.set_postfix(loss=f"{loss.item():.4f}")
            
        # Validation
        model.eval()
        correct = 0
        total = 0
        with torch.no_grad():
            for batch in val_loader:
                batch = {k: v.to(device) for k, v in batch.items()}
                outputs = model(**batch)
                preds = outputs.logits.argmax(dim=-1)
                correct += (preds == batch["labels"]).sum().item()
                total += batch["labels"].size(0)
                
        val_acc = correct / total if total > 0 else 0.0
        print(f"Epoch {epoch + 1} - Train loss: {total_loss / len(train_loader):.4f} - Val Accuracy: {val_acc:.4f}")
        
    # Save model
    args.output_dir.mkdir(parents=True, exist_ok=True)
    model.save_pretrained(args.output_dir)
    tokenizer.save_pretrained(args.output_dir)
    print(f"Saved relation model to {args.output_dir}")


if __name__ == "__main__":
    main()
