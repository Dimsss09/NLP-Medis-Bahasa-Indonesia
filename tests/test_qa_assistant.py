"""Unit tests for the ClinicalQAAssistant backend service."""

from __future__ import annotations

import unittest
import tempfile
from pathlib import Path
import sys
import json
import networkx as nx
from networkx.readwrite import json_graph

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.qa_assistant import ClinicalQAAssistant


class TestQAAssistant(unittest.TestCase):
    """Validate that the ClinicalQAAssistant retrieves context and generates responses."""

    def setUp(self) -> None:
        self.tmpdir = tempfile.TemporaryDirectory()
        self.tmp_path = Path(self.tmpdir.name)
        
        self.kg_path = self.tmp_path / "test_kg.json"
        self.corpus_path = self.tmp_path / "test_corpus.txt"
        
        # Write mock corpus
        corpus_content = (
            "obat untuk mengatasi gatalgatal pada anak\n"
            "bagaimana cara mengobati penyakit asma bronkial\n"
            "dosis paracetamol 500 mg untuk demam\n"
            "alergi dingin dan cara mengatasinya\n"
        )
        self.corpus_path.write_text(corpus_content, encoding="utf-8")
        
        # Write mock KG
        test_graph = nx.DiGraph()
        # Add paracetamol
        test_graph.add_node("paracetamol", label="OBAT", standard_code="ATC: N02BE01", standard_name="Paracetamol")
        # Add fever
        test_graph.add_node("fever, unspecified", label="GEJALA", standard_code="ICD-10: R50.9", standard_name="Fever, unspecified")
        # Add relationship: paracetamol treats fever
        test_graph.add_edge("paracetamol", "fever, unspecified", type="treats")
        
        data = json_graph.node_link_data(test_graph)
        with self.kg_path.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

        # NER/Assertion/Relation dirs
        self.ner_dir = ROOT_DIR / "models" / "indobert-medical-ner-id"
        self.assertion_dir = ROOT_DIR / "models" / "indobert-medical-assertion-id"
        self.relation_dir = ROOT_DIR / "models" / "indobert-medical-relation-id"
        
        self.models_exist = (
            self.ner_dir.exists() and
            self.assertion_dir.exists() and
            self.relation_dir.exists()
        )

    def tearDown(self) -> None:
        self.tmpdir.cleanup()

    def test_corpus_retrieval(self) -> None:
        if not self.models_exist:
            self.skipTest("Local models not found. Skipping QA assistant tests.")
            
        assistant = ClinicalQAAssistant(
            self.ner_dir, self.assertion_dir, self.relation_dir, 
            self.kg_path, self.corpus_path
        )
        
        # Query: "cara mengobati asma"
        passages = assistant.retrieve_corpus_passages("cara mengobati asma", top_k=2)
        self.assertTrue(len(passages) >= 1)
        self.assertTrue(any("asma bronkial" in p for p in passages))

    def test_kg_context_retrieval(self) -> None:
        if not self.models_exist:
            self.skipTest("Local models not found. Skipping QA assistant tests.")
            
        assistant = ClinicalQAAssistant(
            self.ner_dir, self.assertion_dir, self.relation_dir, 
            self.kg_path, self.corpus_path
        )
        
        # Mock query entities
        entities = [
            {"id": "e1", "text": "paracetamol", "label": "OBAT", "start": 0, "end": 11}
        ]
        
        facts = assistant.retrieve_kg_context(entities)
        self.assertEqual(len(facts), 1)
        self.assertEqual(facts[0]["head"], "Paracetamol")
        self.assertEqual(facts[0]["relation"], "treats")
        self.assertEqual(facts[0]["tail"], "Fever, unspecified")

    def test_fallback_response_generation(self) -> None:
        if not self.models_exist:
            self.skipTest("Local models not found. Skipping QA assistant tests.")
            
        assistant = ClinicalQAAssistant(
            self.ner_dir, self.assertion_dir, self.relation_dir, 
            self.kg_path, self.corpus_path
        )
        
        entities = [{"id": "e1", "text": "parasetamol", "label": "OBAT"}]
        kg_facts = [{"head": "Paracetamol", "relation": "treats", "tail": "Fever"}]
        passages = ["dosis paracetamol 500 mg untuk demam"]
        
        res = assistant.generate_fallback_response("parasetamol", entities, kg_facts, passages)
        self.assertIn("Paracetamol", res)
        self.assertIn("mengobati/meredakan", res)
        self.assertIn("dosis paracetamol", res.lower())


if __name__ == "__main__":
    unittest.main()
