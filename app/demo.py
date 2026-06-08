"""Interactive Streamlit demo for Indonesian medical NER."""

from __future__ import annotations

import html
import sys
from base64 import b64encode
from pathlib import Path

import streamlit as st
import yaml

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.predict import DEFAULT_MODEL_DIR, EntitySpan, load_model, predict_entities


BACKGROUND_IMAGE = ROOT_DIR / "assets" / "medical-ner-background.png"
CONFIG_FILE = ROOT_DIR / "config.yaml"

LABEL_COLORS = {
    "GEJALA": ("#fff1f2", "#be123c"),
    "OBAT": ("#eff6ff", "#1d4ed8"),
    "DOSIS": ("#f0fdf4", "#15803d"),
    "DIAGNOSIS": ("#fefce8", "#a16207"),
    "ANATOMI": ("#f5f3ff", "#6d28d9"),
}


def background_data_uri() -> str:
    """Return the project background image as a CSS-safe data URI."""
    if not BACKGROUND_IMAGE.exists():
        return ""
    encoded = b64encode(BACKGROUND_IMAGE.read_bytes()).decode("ascii")
    return f"data:image/png;base64,{encoded}"


def inject_page_style() -> None:
    """Inject app-level visual polish for the Streamlit demo."""
    image_uri = background_data_uri()
    background_layer = (
        f"linear-gradient(115deg, rgba(8, 15, 23, 0.92), rgba(8, 15, 23, 0.70) 45%, rgba(8, 15, 23, 0.82)), url('{image_uri}')"
        if image_uri
        else "linear-gradient(115deg, #081017, #13232c 48%, #111827)"
    )
    st.markdown(
        f"""
        <style>
        @keyframes logoPulse {{
            0%, 100% {{ transform: scale(1); box-shadow: 0 0 0 0 rgba(45, 212, 191, 0.35); }}
            50% {{ transform: scale(1.035); box-shadow: 0 0 0 12px rgba(45, 212, 191, 0); }}
        }}
        @keyframes scanLine {{
            0% {{ transform: translateX(-110%); opacity: 0; }}
            20% {{ opacity: 0.75; }}
            100% {{ transform: translateX(110%); opacity: 0; }}
        }}
        .stApp {{
            background: {background_layer};
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
            color: #edf7f6;
        }}
        .block-container {{
            padding-top: 2.2rem;
            padding-bottom: 2.8rem;
            max-width: 1180px;
        }}
        [data-testid="stSidebar"] {{
            background: rgba(7, 16, 24, 0.86);
            border-right: 1px solid rgba(148, 163, 184, 0.18);
        }}
        [data-testid="stSidebar"] * {{
            color: #e5f3f2;
        }}
        .brand-shell {{
            position: relative;
            overflow: hidden;
            padding: 1.05rem 1.1rem 1.15rem;
            border: 1px solid rgba(125, 211, 252, 0.24);
            border-radius: 8px;
            background: rgba(7, 15, 23, 0.70);
            backdrop-filter: blur(10px);
        }}
        .brand-shell::after {{
            content: "";
            position: absolute;
            inset: 0;
            width: 55%;
            background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.10), transparent);
            animation: scanLine 5.5s ease-in-out infinite;
            pointer-events: none;
        }}
        .brand-row {{
            display: flex;
            gap: 0.9rem;
            align-items: center;
            position: relative;
            z-index: 1;
        }}
        .brand-logo {{
            width: 58px;
            height: 58px;
            display: grid;
            place-items: center;
            border-radius: 50%;
            border: 1px solid rgba(45, 212, 191, 0.65);
            background:
                radial-gradient(circle at 30% 28%, rgba(251, 113, 133, 0.48), transparent 30%),
                linear-gradient(145deg, rgba(20, 184, 166, 0.24), rgba(14, 165, 233, 0.14));
            color: #ccfbf1;
            font-weight: 800;
            letter-spacing: 0;
            animation: logoPulse 3.2s ease-in-out infinite;
        }}
        .brand-copy h1 {{
            margin: 0;
            font-size: 2.05rem;
            line-height: 1.08;
            color: #f8fafc;
            letter-spacing: 0;
        }}
        .brand-copy p {{
            margin: 0.35rem 0 0;
            max-width: 760px;
            color: #c7d8dd;
            font-size: 0.98rem;
        }}
        .metric-strip {{
            display: flex;
            gap: 0.55rem;
            flex-wrap: wrap;
            margin-top: 0.85rem;
            position: relative;
            z-index: 1;
        }}
        .metric-pill {{
            border: 1px solid rgba(148, 163, 184, 0.20);
            border-radius: 999px;
            padding: 0.35rem 0.65rem;
            color: #dff7f4;
            background: rgba(15, 23, 42, 0.56);
            font-size: 0.82rem;
        }}
        .result-panel {{
            font-size: 1.05rem;
            line-height: 2.2;
            padding: 1rem;
            border-radius: 8px;
            border: 1px solid rgba(148, 163, 184, 0.22);
            background: rgba(248, 250, 252, 0.92);
            color: #172033;
        }}
        mark.entity-mark {{
            padding: 0.16rem 0.38rem;
            border-radius: 0.42rem;
            font-weight: 700;
            line-height: 2;
            border: 1px solid rgba(15, 23, 42, 0.08);
        }}
        mark.entity-mark span {{
            font-size: 0.72rem;
            margin-left: 0.35rem;
            letter-spacing: 0;
            opacity: 0.86;
        }}
        h2, h3, label, .stMarkdown, .stDataFrame {{
            color: #eef7f6;
        }}
        .stTextArea textarea {{
            background: rgba(248, 250, 252, 0.96);
            color: #111827;
            border-radius: 8px;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_brand_header() -> None:
    """Render the animated demo identity and compact status pills."""
    st.markdown(
        """
        <section class="brand-shell">
            <div class="brand-row">
                <div class="brand-logo">NER</div>
                <div class="brand-copy">
                    <h1>Medical NER Bahasa Indonesia</h1>
                    <p>Demo lokal untuk menyorot gejala, obat, dosis, diagnosis, dan anatomi dari teks medis Bahasa Indonesia.</p>
                </div>
            </div>
            <div class="metric-strip">
                <span class="metric-pill">IndoBERT (Utama) F1: 0.9987 (Gold) / 0.9996 (Silver)</span>
                <span class="metric-pill">XLM-R (Pembanding) F1: 0.9762 (Gold) / 0.9718 (Silver)</span>
                <span class="metric-pill">Streamlit Local Demo</span>
                <span class="metric-pill">Labels: GEJALA, OBAT, DOSIS, DIAGNOSIS, ANATOMI</span>
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )


def load_model_options() -> dict[str, str]:
    """Load model display labels and local directories from config.yaml."""
    if not CONFIG_FILE.exists():
        return {"IndoBERT": str(DEFAULT_MODEL_DIR)}

    config = yaml.safe_load(CONFIG_FILE.read_text(encoding="utf-8"))
    configured_models = config.get("models")
    if not configured_models:
        return {"IndoBERT": str(config.get("model", {}).get("output_dir", DEFAULT_MODEL_DIR))}

    return {
        f"{item.get('display_name', key)} ({key})": str(item["output_dir"])
        for key, item in configured_models.items()
    }


@st.cache_resource(show_spinner="Memuat Clinical Pipeline (NER + Relasi + Negasi)...")
def cached_pipeline(ner_dir: str, assertion_dir: str, relation_dir: str):
    """Load the integrated clinical pipeline on CPU for Windows stability."""
    from src.predict_pipeline import ClinicalPipeline
    return ClinicalPipeline(Path(ner_dir), Path(assertion_dir), Path(relation_dir), device="cpu")


def render_highlighted_text(text: str, entities: list[dict]) -> str:
    """Render text with entity highlights and assertion cues as safe HTML."""
    if not text:
        return ""

    html_parts: list[str] = []
    cursor = 0
    for entity in sorted(entities, key=lambda item: item["start"]):
        start = entity["start"]
        end = entity["end"]
        label = entity["label"]
        ent_text = text[start:end]
        assertion = entity.get("assertion", "AFFIRMED")
        
        if start < cursor:
            continue
            
        html_parts.append(html.escape(text[cursor:start]))
        
        background, color = LABEL_COLORS.get(label, ("#f3f4f6", "#374151"))
        
        text_style = ""
        badge_suffix = f" ({label})"
        
        if assertion == "NEGATED":
            text_style = "text-decoration: line-through; opacity: 0.55;"
            badge_suffix = f" ({label} - NEGATED)"
            background = "#e2e8f0"
            color = "#475569"
        elif assertion == "UNCERTAIN":
            text_style = "border-bottom: 2px dotted #ca8a04; font-style: italic;"
            badge_suffix = f" ({label} - UNCERTAIN ❓)"
            
        html_parts.append(
            f"<mark class=\"entity-mark\" style=\"background:{background}; color:{color};\">"
            f"<span style=\"{text_style}\">{html.escape(ent_text)}</span>"
            f"<span>{html.escape(badge_suffix)}</span>"
            f"</mark>"
        )
        cursor = end
        
    html_parts.append(html.escape(text[cursor:]))
    return "".join(html_parts)


def render_entity_table(entities: list[dict]) -> None:
    """Render extracted entities and assertions as a compact table."""
    if not entities:
        st.info("Tidak ada entitas medis yang terdeteksi.")
        return

    rows = [
        {
            "Entitas": entity["text"],
            "Label": entity["label"],
            "Asersi": entity.get("assertion", "-"),
            "Start": entity["start"],
            "End": entity["end"]
        }
        for entity in entities
    ]
    st.dataframe(rows, hide_index=True, width="stretch")


def render_relations_table(relations: list[dict], entities: list[dict]) -> None:
    """Render relations list using a user-friendly layout."""
    if not relations:
        st.info("Tidak ada hubungan medis terstruktur yang terdeteksi di dalam kalimat.")
        return

    ent_map = {ent["id"]: ent for ent in entities}
    rel_type_map = {
        "dosage_of": "Dosis dari 💊",
        "treats": "Mengobati / Meredakan 🩺",
        "located_in": "Lokasi anatomi di 📍"
    }

    rows = []
    for rel in relations:
        head_ent = ent_map.get(rel["head"])
        tail_ent = ent_map.get(rel["tail"])
        if head_ent and tail_ent:
            rows.append({
                "Entitas Asal": f"{head_ent['text']} ({head_ent['label']})",
                "Hubungan": rel_type_map.get(rel["type"], rel["type"]),
                "Entitas Tujuan": f"{tail_ent['text']} ({tail_ent['label']})"
            })

    st.dataframe(rows, hide_index=True, width="stretch")


def render_pyvis_graph(G, height: str = "450px") -> None:
    """Render a NetworkX graph inside Streamlit using PyVis."""
    from src.graph_visualizer import generate_graph_html
    import streamlit.components.v1 as components
    
    html_content = generate_graph_html(G, height=height)
    height_int = int(height.replace("px", ""))
    components.html(html_content, height=height_int + 20, scrolling=True)


def main() -> None:
    """Render the interactive demo with tabbed layout."""
    st.set_page_config(page_title="Medical NLP ID (NER + Relations + KG)", layout="wide")
    inject_page_style()
    render_brand_header()

    model_options = load_model_options()
    selected_model = st.sidebar.selectbox("Model NER", list(model_options))
    model_dir = st.sidebar.text_input("Model directory", model_options[selected_model])
    st.sidebar.caption("Pilih IndoBERT atau XLM-R. Klasifikasi asersi, relasi, dan Knowledge Graph akan menggunakan ekstensi IndoBERT secara otomatis.")

    # Paths for models and global KG
    assertion_dir = ROOT_DIR / "models" / "indobert-medical-assertion-id"
    relation_dir = ROOT_DIR / "models" / "indobert-medical-relation-id"
    kg_path = ROOT_DIR / "data" / "knowledge_graph.json"

    # Initialize clinical pipeline
    pipeline = cached_pipeline(model_dir, str(assertion_dir), str(relation_dir))

    # Tab navigation
    tab_analyzer, tab_kg = st.tabs(["🩺 Clinical Analyzer", "🕸️ Eksplorasi Knowledge Graph"])

    with tab_analyzer:
        # Default text example showing negation and relation
        sample_text = "Pasien mengeluhkan demam tinggi dan sesak napas. Diberi paracetamol 500 mg untuk atasi demam, namun tidak batuk."
        st.markdown("### Analisis Rekam Medis (Single Note)")
        text = st.text_area("Teks Medis Bahasa Indonesia", sample_text, height=120)

        if st.button("Ekstrak Informasi Terstruktur", type="primary") or text:
            # Run pipeline predictions
            result = pipeline.predict(text)
            entities = result["entities"]
            relations = result["relations"]
            
            # Get token-level predictions for NER debugging panel
            token_predictions, _ = predict_entities(text, pipeline.ner_tok, pipeline.ner_model, pipeline.device)
            highlighted = render_highlighted_text(text, entities)

            st.subheader("Hasil Sorotan & Asersi")
            st.markdown(
                f"<div class='result-panel'>{highlighted}</div>",
                unsafe_allow_html=True,
            )

            st.markdown("---")
            
            col_rel, col_ent = st.columns([1.1, 0.9])
            
            with col_rel:
                st.subheader("Hubungan Medis (Relations)")
                render_relations_table(relations, entities)
                
            with col_ent:
                st.subheader("Entitas & Asersi")
                render_entity_table(entities)

            st.markdown("---")
            
            # Local PyVis Graph Visualization
            st.subheader("Visualisasi Hubungan Kasus (Local Graph)")
            if relations:
                import networkx as nx
                from src.knowledge_graph import MedicalKnowledgeGraph
                temp_kg = MedicalKnowledgeGraph()
                
                case_G = nx.DiGraph()
                ent_map = {ent["id"]: ent for ent in entities}
                for rel in relations:
                    h_ent = ent_map.get(rel["head"])
                    t_ent = ent_map.get(rel["tail"])
                    if h_ent and t_ent:
                        h_key, h_label, h_code, h_std_name = temp_kg.normalize_node(h_ent["text"], h_ent["label"])
                        t_key, t_label, t_code, t_std_name = temp_kg.normalize_node(t_ent["text"], t_ent["label"])
                        
                        if h_key not in case_G:
                            case_G.add_node(h_key, label=h_label, standard_code=h_code, standard_name=h_std_name)
                        if t_key not in case_G:
                            case_G.add_node(t_key, label=t_label, standard_code=t_code, standard_name=t_std_name)
                        case_G.add_edge(h_key, t_key, type=rel["type"])
                
                render_pyvis_graph(case_G, height="400px")
                
                # Option to save to Global Knowledge Graph
                col_btn, _ = st.columns([1, 2])
                with col_btn:
                    if st.button("💾 Simpan Hubungan Medis ke Knowledge Graph Global", type="secondary"):
                        pipeline.add_to_graph(result, kg_path)
                        st.success("Fakta medis dari kalimat ini berhasil digabung ke Knowledge Graph global!")
            else:
                st.info("Tidak ada relasi untuk divisualisasikan dalam kalimat ini.")

            st.markdown("---")
            st.subheader("Detail Token NER (Debugging)")
            st.dataframe(
                [{"Token": item.token, "Label": item.label, "Start": item.start, "End": item.end} for item in token_predictions],
                hide_index=True,
                width="stretch",
            )

    with tab_kg:
        st.markdown("### Eksplorasi Global Knowledge Graph")
        
        # Load global KG
        from src.knowledge_graph import MedicalKnowledgeGraph
        global_kg = MedicalKnowledgeGraph()
        global_kg.load_graph(kg_path)
        
        # Stats
        num_nodes = len(global_kg.graph.nodes)
        num_edges = len(global_kg.graph.edges)
        
        col_s1, col_s2, col_s3 = st.columns(3)
        with col_s1:
            st.metric("Total Entitas (Nodes)", num_nodes)
        with col_s2:
            st.metric("Total Hubungan (Edges)", num_edges)
        with col_s3:
            st.metric("Penyimpanan", "Portable JSON File")
            
        st.markdown("---")
        
        col_query, col_viz = st.columns([0.4, 0.6])
        
        with col_query:
            st.subheader("Kueri Medis Terstruktur")
            query_mode = st.radio(
                "Jenis Pencarian",
                [
                    "Cari Obat Berdasarkan Gejala",
                    "Cari Gejala Berdasarkan Obat",
                    "Eksplorasi Detail Simpul Medis"
                ]
            )
            
            if query_mode == "Cari Obat Berdasarkan Gejala":
                # Get symptoms from graph
                symptom_list = sorted(list({
                    data.get("standard_name", node)
                    for node, data in global_kg.graph.nodes(data=True)
                    if data.get("label") in {"GEJALA", "DIAGNOSIS"}
                }))
                
                if symptom_list:
                    selected_symptom = st.selectbox("Pilih Gejala / Keluhan", symptom_list)
                    if st.button("Cari Obat Terkait"):
                        drugs = global_kg.query_drugs_for_symptom(selected_symptom)
                        if drugs:
                            st.success(f"Ditemukan {len(drugs)} obat terkait:")
                            rows = []
                            for d in drugs:
                                rows.append({
                                    "Nama Obat": d["name"],
                                    "Standardisasi Code": d["code"] if d["code"] else "-"
                                })
                            st.dataframe(rows, hide_index=True, width="stretch")
                            
                            # Subgraph visualization
                            st.session_state["kg_explore_node"] = selected_symptom
                        else:
                            st.warning("Tidak ditemukan rekomendasi obat dalam basis data graf.")
                else:
                    st.info("Belum ada gejala medis yang terdaftar di basis data graf.")
                    
            elif query_mode == "Cari Gejala Berdasarkan Obat":
                # Get drugs from graph
                drug_list = sorted(list({
                    data.get("standard_name", node)
                    for node, data in global_kg.graph.nodes(data=True)
                    if data.get("label") == "OBAT"
                }))
                
                if drug_list:
                    selected_drug = st.selectbox("Pilih Obat", drug_list)
                    if st.button("Cari Gejala yang Diobati"):
                        symptoms = global_kg.query_symptoms_for_drug(selected_drug)
                        if symptoms:
                            st.success(f"Obat {selected_drug} mengobati {len(symptoms)} gejala/diagnosis:")
                            rows = []
                            for s in symptoms:
                                rows.append({
                                    "Gejala / Diagnosis": s["name"],
                                    "Kategori": s["label"],
                                    "Standardisasi Code": s["code"] if s["code"] else "-"
                                })
                            st.dataframe(rows, hide_index=True, width="stretch")
                            
                            # Subgraph visualization
                            st.session_state["kg_explore_node"] = selected_drug
                        else:
                            st.warning("Tidak ada relasi gejala medis yang diobati oleh obat ini dalam basis data graf.")
                else:
                    st.info("Belum ada obat yang terdaftar di basis data graf.")
                    
            elif query_mode == "Eksplorasi Detail Simpul Medis":
                # All concepts list
                node_list = sorted(list({
                    data.get("standard_name", node)
                    for node, data in global_kg.graph.nodes(data=True)
                }))
                
                if node_list:
                    selected_node = st.selectbox("Pilih Simpul Medis", node_list)
                    depth = st.slider("Kedalaman Relasi (Depth/Hop)", min_value=1, max_value=3, value=1)
                    if st.button("Visualisasikan Jaringan"):
                        st.session_state["kg_explore_node"] = selected_node
                        st.session_state["kg_explore_depth"] = depth
                else:
                    st.info("Belum ada simpul terdaftar.")
                    
        with col_viz:
            st.subheader("Visualisasi Jaringan Relasi Medis")
            
            # Determine which node to display
            explore_node = st.session_state.get("kg_explore_node")
            explore_depth = st.session_state.get("kg_explore_depth", 1)
            
            if explore_node:
                st.markdown(f"Menampilkan sub-jaringan medis di sekitar: **{explore_node}** (kedalaman: {explore_depth})")
                sub_G = global_kg.query_subgraph(explore_node, depth=explore_depth)
                render_pyvis_graph(sub_G, height="450px")
            else:
                # Fallback to visualizing a small random subgraph or the first drug in the graph
                drug_list = sorted(list({
                    data.get("standard_name", node)
                    for node, data in global_kg.graph.nodes(data=True)
                    if data.get("label") == "OBAT"
                }))
                if drug_list:
                    default_node = drug_list[0]
                    st.markdown(f"Menampilkan sub-jaringan default di sekitar: **{default_node}**")
                    sub_G = global_kg.query_subgraph(default_node, depth=1)
                    render_pyvis_graph(sub_G, height="450px")
                else:
                    st.info("Tambahkan data hubungan di tab Clinical Analyzer untuk mulai melihat visualisasi graf.")


if __name__ == "__main__":
    main()
