"""Unit tests for the integrated ClinicalPipeline."""

from __future__ import annotations

import unittest
from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.predict_pipeline import ClinicalPipeline


class TestPredictPipeline(unittest.TestCase):
    """Validate that the ClinicalPipeline performs joint extraction."""

    @classmethod
    def setUpClass(cls):
        # Directories to models
        cls.ner_dir = ROOT_DIR / "models" / "indobert-medical-ner-id"
        cls.assertion_dir = ROOT_DIR / "models" / "indobert-medical-assertion-id"
        cls.relation_dir = ROOT_DIR / "models" / "indobert-medical-relation-id"

        # Check if all model folders exist before attempting to load
        cls.models_exist = (
            cls.ner_dir.exists() and
            cls.assertion_dir.exists() and
            cls.relation_dir.exists()
        )

    def test_pipeline_prediction(self):
        if not self.models_exist:
            self.skipTest("Local models not found in models/ directory. Skipping integrated pipeline test.")

        # Initialize pipeline on CPU
        pipeline = ClinicalPipeline(
            ner_dir=self.ner_dir,
            assertion_dir=self.assertion_dir,
            relation_dir=self.relation_dir,
            device="cpu"
        )

        test_text = "Pasien diberikan paracetamol 500 mg untuk mengobati demam, tetapi tidak mengeluhkan batuk."
        result = pipeline.predict(test_text)

        # Basic structure validation
        self.assertIn("text", result)
        self.assertIn("entities", result)
        self.assertIn("relations", result)
        self.assertEqual(result["text"], test_text)

        # Check that assertions are present for symptoms/diagnosis
        for ent in result["entities"]:
            if ent["label"] in {"GEJALA", "DIAGNOSIS"}:
                self.assertIn("assertion", ent)
                self.assertIn(ent["assertion"], {"AFFIRMED", "NEGATED", "UNCERTAIN"})

        # Check that relations have valid keys
        for rel in result["relations"]:
            self.assertIn("head", rel)
            self.assertIn("tail", rel)
            self.assertIn("type", rel)
            self.assertIn(rel["type"], {"dosage_of", "treats", "located_in"})
