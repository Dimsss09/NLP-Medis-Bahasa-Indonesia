"""Tests for the semi-automatic BIO annotation pipeline."""

from __future__ import annotations

import unittest

from src.annotate_bio import annotate_tokens, load_lexicon, tokenize


class AnnotateBioTest(unittest.TestCase):
    """Validate core BIO annotation behavior."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.lexicon = load_lexicon("resources/medical_lexicon.yaml")

    def test_longest_match_and_bio_labels(self) -> None:
        tokens = tokenize("pasien mengalami nyeri dada sebelah kiri")
        labels = annotate_tokens(tokens, self.lexicon)

        self.assertEqual(
            labels,
            ["O", "O", "B-GEJALA", "I-GEJALA", "I-GEJALA", "I-GEJALA"],
        )

    def test_dosage_pattern(self) -> None:
        tokens = tokenize("minum paracetamol 500 mg sesudah makan")
        labels = annotate_tokens(tokens, self.lexicon)

        self.assertEqual(labels[1], "B-OBAT")
        self.assertEqual(labels[2:4], ["B-DOSIS", "I-DOSIS"])
        self.assertEqual(labels[4:6], ["B-DOSIS", "I-DOSIS"])


if __name__ == "__main__":
    unittest.main()
