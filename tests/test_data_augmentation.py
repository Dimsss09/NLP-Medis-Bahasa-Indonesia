"""Unit tests for the Entity Substitution Data Augmentation logic."""

from __future__ import annotations

import unittest
from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.annotate_bio import Token
from src.build_silver_dataset import substitute_entities


class TestDataAugmentation(unittest.TestCase):
    """Validate that the entity substitution augmentation behaves correctly."""

    def setUp(self) -> None:
        # Mini lexicon mock for testing substitution
        self.mock_lexicon = {
            "OBAT": [("aspirin",), ("metformin",), ("amoxicillin",)],
            "GEJALA": [("nyeri", "dada"), ("demam",), ("mual",)],
            "DOSIS": [("500", "mg"), ("10", "unit")]
        }

    def test_no_entities_returns_empty(self) -> None:
        # Text: "Pasien sehat walafiat."
        tokens = [
            Token("Pasien", 0, 6),
            Token("sehat", 7, 12),
            Token("walafiat", 13, 21),
            Token(".", 21, 22)
        ]
        labels = ["O", "O", "O", "O"]
        
        result = substitute_entities(tokens, labels, self.mock_lexicon, num_augmentations=3)
        self.assertEqual(len(result), 0)

    def test_single_entity_substitution(self) -> None:
        # Text: "Pasien minum paracetamol." (paracetamol = B-OBAT)
        tokens = [
            Token("Pasien", 0, 6),
            Token("minum", 7, 12),
            Token("paracetamol", 13, 24),
            Token(".", 24, 25)
        ]
        labels = ["O", "O", "B-OBAT", "O"]
        
        result = substitute_entities(tokens, labels, self.mock_lexicon, num_augmentations=3)
        self.assertEqual(len(result), 3)
        
        for new_tokens, new_labels in result:
            # Check length of labels remains the same for surrounding, but might vary for substitution
            self.assertEqual(new_labels[0], "O")
            self.assertEqual(new_labels[1], "O")
            self.assertEqual(new_labels[-1], "O")
            
            # Check that the substituted word is from our mock lexicon for OBAT
            substituted_words = [t.text for t in new_tokens[2:-1]]
            substituted_phrase = tuple(w.lower() for w in substituted_words)
            self.assertIn(substituted_phrase, self.mock_lexicon["OBAT"])
            
            # Check BIO labels
            entity_labels = new_labels[2:-1]
            self.assertEqual(entity_labels[0], "B-OBAT")
            for lbl in entity_labels[1:]:
                self.assertEqual(lbl, "I-OBAT")

    def test_multi_token_entity_substitution(self) -> None:
        # Text: "Pasien mengeluh nyeri dada kemarin." (nyeri dada = B-GEJALA, I-GEJALA)
        tokens = [
            Token("Pasien", 0, 6),
            Token("mengeluh", 7, 15),
            Token("nyeri", 16, 21),
            Token("dada", 22, 26),
            Token("kemarin", 27, 34)
        ]
        labels = ["O", "O", "B-GEJALA", "I-GEJALA", "O"]
        
        result = substitute_entities(tokens, labels, self.mock_lexicon, num_augmentations=2)
        self.assertEqual(len(result), 2)
        
        for new_tokens, new_labels in result:
            self.assertEqual(new_labels[0], "O")
            self.assertEqual(new_labels[1], "O")
            self.assertEqual(new_labels[-1], "O")
            
            # Find index of B-GEJALA
            b_idx = new_labels.index("B-GEJALA")
            self.assertEqual(b_idx, 2)
            
            # Substituted tokens check
            end_idx = len(new_labels) - 1
            substituted_phrase = tuple(t.text.lower() for t in new_tokens[b_idx:end_idx])
            self.assertIn(substituted_phrase, self.mock_lexicon["GEJALA"])


if __name__ == "__main__":
    unittest.main()
