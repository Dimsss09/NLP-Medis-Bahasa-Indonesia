"""Medical Knowledge Graph manager using NetworkX."""

from __future__ import annotations

import json
from pathlib import Path
import difflib
import networkx as nx
from networkx.readwrite import json_graph

# Kamus standardisasi medis internal (Bahasa Indonesia -> Standar Kode)
CONCEPT_DICTIONARY = {
    # GEJALA / DIAGNOSIS -> ICD-10
    "demam": {"code": "ICD-10: R50.9", "concept": "Fever, unspecified"},
    "panas": {"code": "ICD-10: R50.9", "concept": "Fever, unspecified"},
    "batuk": {"code": "ICD-10: R05", "concept": "Cough"},
    "sesak napas": {"code": "ICD-10: R06.0", "concept": "Dyspnea"},
    "sesak": {"code": "ICD-10: R06.0", "concept": "Dyspnea"},
    "nyeri dada": {"code": "ICD-10: R07.9", "concept": "Chest pain, unspecified"},
    "sakit kepala": {"code": "ICD-10: R51", "concept": "Headache"},
    "pusing": {"code": "ICD-10: R51", "concept": "Headache"},
    "flu": {"code": "ICD-10: J11", "concept": "Influenza, virus not identified"},
    "pilek": {"code": "ICD-10: J11", "concept": "Influenza, virus not identified"},
    "hipertensi": {"code": "ICD-10: I10", "concept": "Essential hypertension"},
    "darah tinggi": {"code": "ICD-10: I10", "concept": "Essential hypertension"},
    "diabetes": {"code": "ICD-10: E11", "concept": "Type 2 diabetes mellitus"},
    "kencing manis": {"code": "ICD-10: E11", "concept": "Type 2 diabetes mellitus"},
    "asma": {"code": "ICD-10: J45", "concept": "Asthma"},
    
    # OBAT -> ATC
    "paracetamol": {"code": "ATC: N02BE01", "concept": "Paracetamol"},
    "parasetamol": {"code": "ATC: N02BE01", "concept": "Paracetamol"},
    "panadol": {"code": "ATC: N02BE01", "concept": "Paracetamol"},
    "amoxicillin": {"code": "ATC: J01CA04", "concept": "Amoxicillin"},
    "amoksisilin": {"code": "ATC: J01CA04", "concept": "Amoxicillin"},
    "ibuprofen": {"code": "ATC: M01AE01", "concept": "Ibuprofen"},
    "metformin": {"code": "ATC: A10BA02", "concept": "Metformin"},
    "aspirin": {"code": "ATC: N02BA01", "concept": "Acetylsalicylic acid"},
}


class MedicalKnowledgeGraph:
    """Manages medical knowledge graph nodes, edges, standardization, and queries."""

    def __init__(self) -> None:
        self.graph = nx.DiGraph()

    def normalize_node(self, name: str, label: str) -> tuple[str, str, str | None, str]:
        """Normalize node name and map to standard concept code (ICD-10 / ATC) if available.
        
        Returns:
            Tuple of (node_key, label, standard_code, standard_name)
        """
        cleaned_name = name.strip().lower()
        
        # 1. Check direct match
        match_info = CONCEPT_DICTIONARY.get(cleaned_name)
        
        # 2. Check fuzzy match if no direct match for GEJALA/DIAGNOSIS/OBAT
        if not match_info and label in {"GEJALA", "DIAGNOSIS", "OBAT"}:
            close_matches = difflib.get_close_matches(cleaned_name, CONCEPT_DICTIONARY.keys(), n=1, cutoff=0.75)
            if close_matches:
                match_info = CONCEPT_DICTIONARY[close_matches[0]]
                
        if match_info:
            # Resolve to standard concept name as the node key
            node_key = match_info["concept"].lower()
            return node_key, label, match_info["code"], match_info["concept"]
        else:
            # Return cleaned name itself
            return cleaned_name, label, None, name.strip().title()

    def add_fact(self, head_name: str, head_label: str, relation: str, tail_name: str, tail_label: str) -> None:
        """Add a medical relation triple to the knowledge graph with normalization."""
        h_key, h_label, h_code, h_std_name = self.normalize_node(head_name, head_label)
        t_key, t_label, t_code, t_std_name = self.normalize_node(tail_name, tail_label)
        
        # Add head node
        if h_key not in self.graph:
            self.graph.add_node(h_key, label=h_label, standard_code=h_code, standard_name=h_std_name)
        else:
            # Update attributes if they exist
            if h_code and not self.graph.nodes[h_key].get("standard_code"):
                self.graph.nodes[h_key]["standard_code"] = h_code
                self.graph.nodes[h_key]["standard_name"] = h_std_name
                
        # Add tail node
        if t_key not in self.graph:
            self.graph.add_node(t_key, label=t_label, standard_code=t_code, standard_name=t_std_name)
        else:
            if t_code and not self.graph.nodes[t_key].get("standard_code"):
                self.graph.nodes[t_key]["standard_code"] = t_code
                self.graph.nodes[t_key]["standard_name"] = t_std_name
                
        # Add relation edge
        self.graph.add_edge(h_key, t_key, type=relation)

    def save_graph(self, filepath: Path) -> None:
        """Save the knowledge graph to a JSON file."""
        filepath.parent.mkdir(parents=True, exist_ok=True)
        data = json_graph.node_link_data(self.graph)
        with filepath.open("w", encoding="utf-8") as file:
            json.dump(data, file, indent=2, ensure_ascii=False)

    def load_graph(self, filepath: Path) -> None:
        """Load the knowledge graph from a JSON file."""
        if not filepath.exists():
            # Initialize empty graph
            self.graph = nx.DiGraph()
            return
            
        with filepath.open("r", encoding="utf-8") as file:
            data = json.load(file)
        self.graph = json_graph.node_link_graph(data)

    def query_drugs_for_symptom(self, symptom_name: str) -> list[dict]:
        """Find drugs that treat a given symptom/diagnosis."""
        normalized_symptom, _, _, _ = self.normalize_node(symptom_name, "GEJALA")
        results = []
        
        if normalized_symptom not in self.graph:
            return results
            
        # In-edges to symptom with type 'treats'
        for u, v, data in self.graph.in_edges(normalized_symptom, data=True):
            if data.get("type") == "treats":
                node_data = self.graph.nodes[u]
                results.append({
                    "name": node_data.get("standard_name", u),
                    "code": node_data.get("standard_code"),
                    "key": u
                })
        return results

    def query_symptoms_for_drug(self, drug_name: str) -> list[dict]:
        """Find symptoms/diagnoses treated by a given drug."""
        normalized_drug, _, _, _ = self.normalize_node(drug_name, "OBAT")
        results = []
        
        if normalized_drug not in self.graph:
            return results
            
        # Out-edges from drug with type 'treats'
        for u, v, data in self.graph.out_edges(normalized_drug, data=True):
            if data.get("type") == "treats":
                node_data = self.graph.nodes[v]
                results.append({
                    "name": node_data.get("standard_name", v),
                    "code": node_data.get("standard_code"),
                    "key": v,
                    "label": node_data.get("label", "GEJALA")
                })
        return results

    def query_subgraph(self, center_node: str, depth: int = 1) -> nx.DiGraph:
        """Extract a subgraph centered around a specific node up to a certain depth."""
        # Convert node name to key
        center_key = center_node.strip().lower()
        if center_key not in self.graph:
            # Check if standard concept maps to it
            matched_key, _, _, _ = self.normalize_node(center_node, "OBAT")
            if matched_key in self.graph:
                center_key = matched_key
            else:
                # Search nodes standard_name
                found = False
                for node, data in self.graph.nodes(data=True):
                    if data.get("standard_name", "").lower() == center_key:
                        center_key = node
                        found = True
                        break
                if not found:
                    return nx.DiGraph()

        # Gather nodes within depth
        nodes = {center_key}
        current_layer = {center_key}
        
        for _ in range(depth):
            next_layer = set()
            for node in current_layer:
                # Successors and predecessors (undirected neighbors)
                neighbors = set(self.graph.successors(node)) | set(self.graph.predecessors(node))
                next_layer.update(neighbors)
            next_layer.difference_update(nodes)
            if not next_layer:
                break
            nodes.update(next_layer)
            current_layer = next_layer
            
        return self.graph.subgraph(nodes).copy()
