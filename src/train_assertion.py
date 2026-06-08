"""Train an assertion status classifier (Negation and Uncertainty) using IndoBERT."""

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
DEFAULT_OUTPUT_DIR = Path("models/indobert-medical-assertion-id")

ASSERTION_MAP = {"AFFIRMED": 0, "NEGATED": 1, "UNCERTAIN": 2}
INV_ASSERTION_MAP = {v: k for k, v in ASSERTION_MAP.items()}


def set_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


class AssertionDataset(Dataset):
    def __init__(self, encodings, labels):
        self.encodings = encodings
        self.labels = labels

    def __getitem__(self, idx):
        item = {key: torch.tensor(val[idx]) for key, val in self.encodings.items()}
        item["labels"] = torch.tensor(self.labels[idx], dtype=torch.long)
        return item

    def __len__(self):
        return len(self.labels)


def load_assertion_samples(json_path: Path) -> list[dict]:
    """Load and format assertion samples from JSON dataset."""
    samples = []
    with json_path.open("r", encoding="utf-8") as file:
        records = json.load(file)
        
    for rec in records:
        text = rec["text"]
        for ent in rec["entities"]:
            if "assertion" in ent:
                start = ent["start"]
                end = ent["end"]
                label_str = ent["assertion"]
                label_id = ASSERTION_MAP[label_str]
                
                # Insert entity markers
                modified_text = text[:start] + "[START_ENT] " + text[start:end] + " [END_ENT]" + text[end:]
                samples.append({
                    "text": modified_text,
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
    train_samples = load_assertion_samples(args.train_file)
    val_samples = load_assertion_samples(args.val_file)
    print(f"Loaded {len(train_samples)} training samples, {len(val_samples)} validation samples")
    
    # Initialize tokenizer and model
    tokenizer = AutoTokenizer.from_pretrained(DEFAULT_MODEL_NAME)
    # Add special tokens
    special_tokens = {"additional_special_tokens": ["[START_ENT]", "[END_ENT]"]}
    tokenizer.add_special_tokens(special_tokens)
    
    model = AutoModelForSequenceClassification.from_pretrained(DEFAULT_MODEL_NAME, num_labels=3)
    model.resize_token_embeddings(len(tokenizer))
    
    # Set labels in config
    model.config.id2label = INV_ASSERTION_MAP
    model.config.label2id = ASSERTION_MAP
    
    # Tokenize
    train_texts = [s["text"] for s in train_samples]
    train_labels = [s["label"] for s in train_samples]
    val_texts = [s["text"] for s in val_samples]
    val_labels = [s["label"] for s in val_samples]
    
    train_encodings = tokenizer(train_texts, truncation=True, padding=True, max_length=256)
    val_encodings = tokenizer(val_texts, truncation=True, padding=True, max_length=256)
    
    train_dataset = AssertionDataset(train_encodings, train_labels)
    val_dataset = AssertionDataset(val_encodings, val_labels)
    
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
    print(f"Saved assertion model to {args.output_dir}")


if __name__ == "__main__":
    main()
