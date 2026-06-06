"""Tests for prediction post-processing helpers."""

from __future__ import annotations

import unittest

from src.predict import TokenPrediction, extract_entities


class PredictPostProcessingTest(unittest.TestCase):
    """Validate BIO spans rendered by the demo."""

    def test_extract_multi_token_entity(self) -> None:
        text = "Pasien minum paracetamol sesudah makan."
        predictions = [
            TokenPrediction("Pasien", "O", 0, 6),
            TokenPrediction("minum", "O", 7, 12),
            TokenPrediction("paracetamol", "B-OBAT", 13, 24),
            TokenPrediction("sesudah", "B-DOSIS", 25, 32),
            TokenPrediction("makan", "I-DOSIS", 33, 38),
            TokenPrediction(".", "O", 38, 39),
        ]

        entities = extract_entities(text, predictions)

        self.assertEqual([(entity.text, entity.label) for entity in entities], [("paracetamol", "OBAT"), ("sesudah makan", "DOSIS")])


if __name__ == "__main__":
    unittest.main()
