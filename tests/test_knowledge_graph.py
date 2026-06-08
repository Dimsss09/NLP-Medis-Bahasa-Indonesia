"""Unit tests for the MedicalKnowledgeGraph class."""

from __future__ import annotations

import unittest
from pathlib import Path
import tempfile
import sys

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.knowledge_graph import MedicalKnowledgeGraph


class TestMedicalKnowledgeGraph(unittest.TestCase):
    """Validate that the MedicalKnowledgeGraph normalizes concepts and queries correctly."""

    def setUp(self) -> None:
        self.kg = MedicalKnowledgeGraph()

    def test_normalization_exact_match(self) -> None:
        # Test direct matching in concept dictionary (case-insensitive)
        node_key, label, code, std_name = self.kg.normalize_node("demam", "GEJALA")
        self.assertEqual(node_key, "fever, unspecified")
        self.assertEqual(label, "GEJALA")
        self.assertEqual(code, "ICD-10: R50.9")
        self.assertEqual(std_name, "Fever, unspecified")

        node_key2, label2, code2, std_name2 = self.kg.normalize_node("Parasetamol", "OBAT")
        self.assertEqual(node_key2, "paracetamol")
        self.assertEqual(label2, "OBAT")
        self.assertEqual(code2, "ATC: N02BE01")
        self.assertEqual(std_name2, "Paracetamol")

    def test_normalization_fuzzy_match(self) -> None:
        # Test fuzzy matching using string similarity
        node_key, label, code, std_name = self.kg.normalize_node("paracetamoll", "OBAT")
        self.assertEqual(node_key, "paracetamol")
        self.assertEqual(code, "ATC: N02BE01")
        self.assertEqual(std_name, "Paracetamol")

    def test_normalization_no_match(self) -> None:
        # Test unmatched custom entities
        node_key, label, code, std_name = self.kg.normalize_node("penyakit misterius", "DIAGNOSIS")
        self.assertEqual(node_key, "penyakit misterius")
        self.assertIsNone(code)
        self.assertEqual(std_name, "Penyakit Misterius")

    def test_add_fact_and_edges(self) -> None:
        # Add a fact relation
        self.kg.add_fact(
            head_name="paracetamol", head_label="OBAT",
            relation="treats",
            tail_name="panas", tail_label="GEJALA"
        )
        
        # Both "paracetamol" and "panas" should resolve to their standard keys
        self.assertIn("paracetamol", self.kg.graph)
        self.assertIn("fever, unspecified", self.kg.graph)
        
        # Edge check
        self.assertTrue(self.kg.graph.has_edge("paracetamol", "fever, unspecified"))
        edge_data = self.kg.graph.get_edge_data("paracetamol", "fever, unspecified")
        self.assertEqual(edge_data["type"], "treats")

    def test_graph_serialization(self) -> None:
        self.kg.add_fact("metformin", "OBAT", "treats", "diabetes", "DIAGNOSIS")
        
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = Path(tmpdir) / "kg.json"
            
            # Save
            self.kg.save_graph(filepath)
            self.assertTrue(filepath.exists())
            
            # Load into new instance
            new_kg = MedicalKnowledgeGraph()
            new_kg.load_graph(filepath)
            
            self.assertIn("metformin", new_kg.graph)
            self.assertIn("type 2 diabetes mellitus", new_kg.graph)
            self.assertTrue(new_kg.graph.has_edge("metformin", "type 2 diabetes mellitus"))

    def test_queries(self) -> None:
        self.kg.add_fact("paracetamol", "OBAT", "treats", "demam", "GEJALA")
        self.kg.add_fact("ibuprofen", "OBAT", "treats", "demam", "GEJALA")
        self.kg.add_fact("paracetamol", "OBAT", "treats", "sakit kepala", "GEJALA")
        self.kg.add_fact("500 mg", "DOSIS", "dosage_of", "paracetamol", "OBAT")

        # Query drugs for symptom
        drugs = self.kg.query_drugs_for_symptom("demam")
        drug_names = {d["name"] for d in drugs}
        self.assertEqual(drug_names, {"Paracetamol", "Ibuprofen"})

        # Query symptoms for drug
        symptoms = self.kg.query_symptoms_for_drug("paracetamol")
        symptom_names = {s["name"] for s in symptoms}
        self.assertEqual(symptom_names, {"Fever, unspecified", "Headache"})

    def test_query_subgraph(self) -> None:
        self.kg.add_fact("paracetamol", "OBAT", "treats", "demam", "GEJALA")
        self.kg.add_fact("500 mg", "DOSIS", "dosage_of", "paracetamol", "OBAT")
        self.kg.add_fact("ibuprofen", "OBAT", "treats", "demam", "GEJALA")
        
        sub = self.kg.query_subgraph("paracetamol", depth=1)
        self.assertIn("paracetamol", sub)
        self.assertIn("fever, unspecified", sub)
        self.assertIn("500 mg", sub)
        self.assertNotIn("ibuprofen", sub)  # ibuprofen is connected to demam, but is depth 2 from paracetamol
        
        sub2 = self.kg.query_subgraph("paracetamol", depth=2)
        self.assertIn("ibuprofen", sub2)  # Connected through demam node at depth 2
        
        # Test matching by non-key input
        sub3 = self.kg.query_subgraph("parasetamol", depth=1)
        self.assertIn("paracetamol", sub3)


if __name__ == "__main__":
    unittest.main()
