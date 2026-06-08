"""Clinical QA Assistant combining RAG (TF-IDF over corpus) and Medical Knowledge Graph."""

from __future__ import annotations

import json
import os
import sys
import urllib.request
import urllib.error
from pathlib import Path
import difflib

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.predict_pipeline import ClinicalPipeline
from src.knowledge_graph import MedicalKnowledgeGraph
from src.annotate_bio import Token


class ClinicalQAAssistant:
    def __init__(self, ner_dir: Path, assertion_dir: Path, relation_dir: Path, kg_path: Path, corpus_path: Path):
        self.kg_path = kg_path
        self.corpus_path = corpus_path
        
        # 1. Load Clinical Pipeline (NER + assertion + relation)
        print("Loading Clinical Pipeline for QA Assistant...")
        self.pipeline = ClinicalPipeline(ner_dir, assertion_dir, relation_dir, device="cpu")
        
        # 2. Load Knowledge Graph
        print("Loading Knowledge Graph...")
        self.kg = MedicalKnowledgeGraph()
        self.kg.load_graph(self.kg_path)
        
        # 3. Load Corpus and Initialize TF-IDF index
        print("Initializing TF-IDF index over medical corpus...")
        self.corpus_lines = []
        if self.corpus_path.exists():
            with self.corpus_path.open("r", encoding="utf-8") as f:
                self.corpus_lines = [line.strip() for line in f if line.strip()]
        else:
            print(f"Warning: Corpus file not found at {self.corpus_path}")
            
        if self.corpus_lines:
            self.vectorizer = TfidfVectorizer()
            self.tfidf_matrix = self.vectorizer.fit_transform(self.corpus_lines)
        else:
            self.vectorizer = None
            self.tfidf_matrix = None

    def retrieve_kg_context(self, query_entities: list[dict]) -> list[dict]:
        """Query the knowledge graph for facts related to the query entities."""
        facts = []
        seen_triples = set()
        
        for ent in query_entities:
            ent_text = ent["text"]
            ent_label = ent["label"]
            
            # Normalize key
            h_key, h_label, h_code, h_std_name = self.kg.normalize_node(ent_text, ent_label)
            
            # If the normalized key is in the graph, fetch edges
            matched_key = None
            if h_key in self.kg.graph:
                matched_key = h_key
            else:
                # Fuzzy match node standard names
                for node, ndata in self.kg.graph.nodes(data=True):
                    std_name = ndata.get("standard_name", "").lower()
                    if std_name == h_key or ent_text.lower() in std_name:
                        matched_key = node
                        break
                        
            if matched_key:
                # Get outgoing edges (head)
                for u, v, data in self.kg.graph.out_edges(matched_key, data=True):
                    triple = (u, data.get("type"), v)
                    if triple not in seen_triples:
                        u_data = self.kg.graph.nodes[u]
                        v_data = self.kg.graph.nodes[v]
                        facts.append({
                            "head": u_data.get("standard_name", u),
                            "head_label": u_data.get("label", ""),
                            "relation": data.get("type"),
                            "tail": v_data.get("standard_name", v),
                            "tail_label": v_data.get("label", "")
                        })
                        seen_triples.add(triple)
                        
                # Get incoming edges (tail)
                for u, v, data in self.kg.graph.in_edges(matched_key, data=True):
                    triple = (u, data.get("type"), v)
                    if triple not in seen_triples:
                        u_data = self.kg.graph.nodes[u]
                        v_data = self.kg.graph.nodes[v]
                        facts.append({
                            "head": u_data.get("standard_name", u),
                            "head_label": u_data.get("label", ""),
                            "relation": data.get("type"),
                            "tail": v_data.get("standard_name", v),
                            "tail_label": v_data.get("label", "")
                        })
                        seen_triples.add(triple)
                        
        return facts

    def retrieve_corpus_passages(self, query: str, top_k: int = 5) -> list[str]:
        """Retrieve top-K matching sentences from the text corpus using TF-IDF."""
        if not self.corpus_lines or not self.vectorizer or self.tfidf_matrix is None:
            return []
            
        query_vec = self.vectorizer.transform([query])
        similarities = cosine_similarity(query_vec, self.tfidf_matrix).flatten()
        top_indices = np.argsort(similarities)[::-1][:top_k]
        
        results = []
        for idx in top_indices:
            if similarities[idx] > 0.05:  # Filter out totally unrelated lines
                results.append(self.corpus_lines[idx])
        return results

    def call_gemini_api(self, prompt: str, api_key: str) -> str:
        """Call the Google Gemini API using native HTTP request."""
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
        headers = {"Content-Type": "application/json"}
        data = {
            "contents": [
                {
                    "parts": [
                        {"text": prompt}
                    ]
                }
            ]
        }
        
        req = urllib.request.Request(
            url, 
            data=json.dumps(data).encode("utf-8"), 
            headers=headers, 
            method="POST"
        )
        
        try:
            with urllib.request.urlopen(req) as response:
                res = json.loads(response.read().decode("utf-8"))
                return res["candidates"][0]["content"]["parts"][0]["text"]
        except Exception as e:
            return f"Error calling Gemini API: {str(e)}"

    def call_ollama_api(self, prompt: str, ollama_url: str, model_name: str = "llama3") -> str:
        """Call a local Ollama instance using native HTTP request."""
        headers = {"Content-Type": "application/json"}
        data = {
            "model": model_name,
            "prompt": prompt,
            "stream": False
        }
        
        req = urllib.request.Request(
            f"{ollama_url.rstrip('/')}/api/generate",
            data=json.dumps(data).encode("utf-8"),
            headers=headers,
            method="POST"
        )
        
        try:
            with urllib.request.urlopen(req) as response:
                res = json.loads(response.read().decode("utf-8"))
                return res["response"]
        except Exception as e:
            return f"Error calling Ollama API: {str(e)}. Pastikan Ollama berjalan di endpoint tersebut."

    def generate_fallback_response(self, query: str, entities: list[dict], kg_facts: list[dict], passages: list[str]) -> str:
        """Synthesize a structured clinical response offline if no LLM API is available."""
        lines = ["**[Offline Mode - Asisten Klinis Hibrida]**", ""]
        
        if not entities and not kg_facts and not passages:
            return "Maaf, saya tidak menemukan informasi medis yang relevan untuk kueri Anda di dalam Knowledge Graph maupun korpus teks."
            
        if entities:
            ent_list = [f"**{e['text']}** ({e['label']})" for e in entities]
            lines.append(f"🔍 **Entitas Medis yang Terdeteksi:** {', '.join(ent_list)}")
            lines.append("")
            
        if kg_facts:
            lines.append("🕸️ **Fakta dari Knowledge Graph Medis:**")
            for fact in kg_facts:
                rel_text = {
                    "dosage_of": "memiliki dosis",
                    "treats": "digunakan untuk mengobati/meredakan",
                    "located_in": "berlokasi di"
                }.get(fact["relation"], fact["relation"])
                lines.append(f"- **{fact['head']}** {rel_text} **{fact['tail']}**")
            lines.append("")
            
        if passages:
            lines.append("📖 **Catatan Referensi Klinis Terkait:**")
            for idx, p in enumerate(passages[:3]):
                lines.append(f"{idx+1}. *{p.capitalize()}*")
            lines.append("")
            
        lines.append("💡 *Catatan: Aktifkan API Key Gemini atau jalankan Ollama untuk mendapatkan sintesis bahasa alami yang lebih interaktif.*")
        return "\n".join(lines)

    def answer_query(self, query: str, api_key: str | None = None, ollama_url: str | None = None, ollama_model: str = "llama3") -> dict:
        """Process query, retrieve facts & texts, and synthesize response."""
        # 1. Run Pipeline (NER + Assertions)
        res_pipeline = self.pipeline.predict(query)
        entities = res_pipeline.get("entities", [])
        
        # 2. Retrieve structured context from KG
        kg_facts = self.retrieve_kg_context(entities)
        
        # 3. Retrieve matching text passages
        passages = self.retrieve_corpus_passages(query, top_k=5)
        
        # 4. Construct prompt
        context_str = ""
        if kg_facts:
            context_str += "Fakta Medis dari Graf Pengetahuan:\n"
            for f in kg_facts:
                context_str += f"- {f['head']} -> {f['relation']} -> {f['tail']}\n"
        if passages:
            context_str += "\nDokumen/Catatan Medis Terkait:\n"
            for p in passages:
                context_str += f"- {p}\n"
                
        prompt = f"""Anda adalah seorang Asisten Klinis Medis kecerdasan buatan (AI Clinical Assistant) untuk Bahasa Indonesia.
Tugas Anda adalah menjawab kueri/pertanyaan medis pengguna berdasarkan konteks medis terstruktur dan catatan referensi klinis yang diberikan.

Kueri Pengguna: "{query}"

Konteks Terstruktur & Catatan Referensi:
{context_str if context_str else "(Tidak ada referensi eksternal)"}

Aturan Menjawab:
1. Jawablah secara ramah, profesional, dan dalam Bahasa Indonesia yang baik dan terstruktur.
2. Sintesis jawaban Anda dengan memanfaatkan Fakta Medis Graf Pengetahuan dan Catatan Referensi jika ada.
3. Sebutkan secara jelas entitas medis (seperti obat, gejala, diagnosis) yang Anda temukan.
4. Jika informasi tidak terdapat dalam referensi, gunakan pengetahuan medis umum Anda tetapi berikan catatan/rujukan bahwa itu di luar data lokal.
5. Berikan rujukan sumber referensi di bagian akhir jawaban Anda secara terstruktur.
6. Berikan disclaimer medis di akhir jawaban bahwa informasi ini adalah asisten kecerdasan buatan dan bukan pengganti dokter profesional.

Jawaban Asisten Klinis:"""

        # 5. Synthesize response
        response_text = ""
        source_type = "fallback"
        
        # Try Gemini API key first
        effective_gemini_key = api_key or os.environ.get("GEMINI_API_KEY")
        
        if effective_gemini_key:
            response_text = self.call_gemini_api(prompt, effective_gemini_key)
            source_type = "gemini"
        elif ollama_url:
            response_text = self.call_ollama_api(prompt, ollama_url, ollama_model)
            source_type = "ollama"
        else:
            response_text = self.generate_fallback_response(query, entities, kg_facts, passages)
            source_type = "fallback"
            
        return {
            "query": query,
            "response": response_text,
            "entities": entities,
            "kg_facts": kg_facts,
            "passages": passages,
            "source_type": source_type
        }
