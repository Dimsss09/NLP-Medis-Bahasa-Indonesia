"""Unit tests for the hybrid inference pipeline fallback matcher."""

from __future__ import annotations

import unittest
from pathlib import Path
import tempfile
import sys
import yaml

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.predict_pipeline import run_hybrid_fallback, run_hybrid_relations


class TestHybridPipeline(unittest.TestCase):
    """Validate that the hybrid fallback matching logic behaves correctly."""

    def setUp(self) -> None:
        # Create a temporary lexicon file
        self.tmpdir = tempfile.TemporaryDirectory()
        self.lexicon_path = Path(self.tmpdir.name) / "test_lexicon.yaml"
        
        test_lexicon = {
            "GEJALA": ["demam", "nyeri dada"],
            "OBAT": ["paracetamol", "aspirin", "insulin"],
            "DIAGNOSIS": ["hipertensi", "infark miokard akut"],
            "ANATOMI": ["dada", "bahu"]
        }
        
        with self.lexicon_path.open("w", encoding="utf-8") as f:
            yaml.dump(test_lexicon, f)

    def tearDown(self) -> None:
        self.tmpdir.cleanup()

    def test_pure_lexicon_and_regex_matching(self) -> None:
        # Test matching on raw text with NO pre-existing NER entities
        text = "Diberikan aspirin 80 mg segera untuk meredakan nyeri dada di bahu, dan insulin 10 unit."
        entities = []
        
        result = run_hybrid_fallback(text, entities, self.lexicon_path)
        
        # We expect:
        # - aspirin (OBAT)
        # - 80 mg (DOSIS)
        # - nyeri dada (GEJALA) - note: 'dada' is ANATOMI but 'nyeri dada' is GEJALA and longer, longest match wins
        # - bahu (ANATOMI)
        # - insulin (OBAT)
        # - 10 unit (DOSIS)
        
        # Verify IDs are sorted and sequential e1, e2, ...
        self.assertEqual([e["id"] for e in result], ["e1", "e2", "e3", "e4", "e5", "e6"])
        
        # Verify text mappings
        texts_and_labels = [(e["text"], e["label"]) for e in result]
        self.assertIn(("aspirin", "OBAT"), texts_and_labels)
        self.assertIn(("80 mg", "DOSIS"), texts_and_labels)
        self.assertIn(("nyeri dada", "GEJALA"), texts_and_labels)
        self.assertIn(("bahu", "ANATOMI"), texts_and_labels)
        self.assertIn(("insulin", "OBAT"), texts_and_labels)
        self.assertIn(("10 unit", "DOSIS"), texts_and_labels)

    def test_no_overlap_with_ner_entities(self) -> None:
        text = "Diberikan aspirin 80 mg segera."
        # Simulating that NER model successfully extracted 'aspirin'
        ner_entities = [
            {"id": "e1", "text": "aspirin", "label": "OBAT", "start": 10, "end": 17}
        ]
        
        result = run_hybrid_fallback(text, ner_entities, self.lexicon_path)
        
        # Verify 'aspirin' was not duplicated or overwritten
        # But '80 mg' should be successfully injected as DOSIS
        self.assertEqual(len(result), 2)
        
        texts = [e["text"] for e in result]
        self.assertIn("aspirin", texts)
        self.assertIn("80 mg", texts)
        
        # Ensure sequential ids are maintained
        self.assertEqual(result[0]["id"], "e1")
        self.assertEqual(result[1]["id"], "e2")

    def test_dosage_frequency_patterns(self) -> None:
        text = "Minum parasetamol 3x sehari."
        entities = []
        result = run_hybrid_fallback(text, entities, self.lexicon_path)
        
        # 3x sehari should be matched as DOSIS
        dosages = [e for e in result if e["label"] == "DOSIS"]
        self.assertEqual(len(dosages), 1)
        self.assertEqual(dosages[0]["text"], "3x sehari")

    def test_hybrid_relations(self) -> None:
        text = "Pasien diberikan paracetamol 500 mg untuk mengobati demam, tetapi tidak mengeluhkan batuk."
        entities = [
            {"id": "e1", "text": "paracetamol", "label": "OBAT", "start": 17, "end": 28},
            {"id": "e2", "text": "500 mg", "label": "DOSIS", "start": 29, "end": 35},
            {"id": "e3", "text": "demam", "label": "GEJALA", "start": 51, "end": 56},
            {"id": "e4", "text": "batuk", "label": "GEJALA", "start": 84, "end": 89}
        ]
        
        existing_relations = []
        relations = run_hybrid_relations(text, entities, existing_relations)
        
        self.assertTrue(len(relations) >= 2)
        
        rel_types = {(r["head"], r["tail"], r["type"]) for r in relations}
        self.assertIn(("e2", "e1", "dosage_of"), rel_types)
        self.assertIn(("e1", "e3", "treats"), rel_types)


if __name__ == "__main__":
    unittest.main()
