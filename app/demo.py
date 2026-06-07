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


@st.cache_resource(show_spinner="Memuat model NER...")
def cached_model(model_dir: str):
    """Load model once per Streamlit session (Forced CPU for Windows stability)."""
    import torch
    from transformers import AutoModelForTokenClassification, AutoTokenizer
    model_path = Path(model_dir)
    tokenizer = AutoTokenizer.from_pretrained(model_path)
    model = AutoModelForTokenClassification.from_pretrained(model_path)
    device = torch.device("cpu")
    model.to(device)
    model.eval()
    return tokenizer, model, device


def render_highlighted_text(text: str, entities: list[EntitySpan]) -> str:
    """Render text with entity highlights as safe HTML."""
    if not text:
        return ""

    html_parts: list[str] = []
    cursor = 0
    for entity in sorted(entities, key=lambda item: item.start):
        if entity.start < cursor:
            continue
        html_parts.append(html.escape(text[cursor:entity.start]))
        background, color = LABEL_COLORS.get(entity.label, ("#f3f4f6", "#374151"))
        html_parts.append(
            "<mark class=\"entity-mark\" style=\""
            f"background:{background}; color:{color}; "
            "\">"
            f"{html.escape(text[entity.start:entity.end])}"
            f"<span>{html.escape(entity.label)}</span>"
            "</mark>"
        )
        cursor = entity.end
    html_parts.append(html.escape(text[cursor:]))
    return "".join(html_parts)


def render_entity_table(entities: list[EntitySpan]) -> None:
    """Render extracted entities as a compact table."""
    if not entities:
        st.info("Tidak ada entitas medis yang terdeteksi.")
        return

    rows = [
        {"Entitas": entity.text, "Label": entity.label, "Start": entity.start, "End": entity.end}
        for entity in entities
    ]
    st.dataframe(rows, hide_index=True, width="stretch")


def main() -> None:
    """Render the interactive demo."""
    st.set_page_config(page_title="Medical NER ID", layout="wide")
    inject_page_style()
    render_brand_header()

    model_options = load_model_options()
    selected_model = st.sidebar.selectbox("Model", list(model_options))
    model_dir = st.sidebar.text_input("Model directory", model_options[selected_model])
    st.sidebar.caption("Pilih IndoBERT sebagai model utama atau XLM-R sebagai model pembanding setelah training selesai.")

    sample_text = "Pasien mengalami demam tinggi, nyeri dada, dan minum paracetamol 500 mg sesudah makan."
    st.markdown("### Input Teks")
    text = st.text_area("Teks medis", sample_text, height=140)

    tokenizer, model, device = cached_model(model_dir)
    if st.button("Ekstrak Entitas", type="primary") or text:
        token_predictions, entities = predict_entities(text, tokenizer, model, device)
        highlighted = render_highlighted_text(text, entities)

        st.subheader("Hasil Sorotan")
        st.markdown(
            f"<div class='result-panel'>{highlighted}</div>",
            unsafe_allow_html=True,
        )

        left, right = st.columns([1, 1])
        with left:
            st.subheader("Entitas")
            render_entity_table(entities)
        with right:
            st.subheader("Token")
            st.dataframe(
                [{"Token": item.token, "Label": item.label, "Start": item.start, "End": item.end} for item in token_predictions],
                hide_index=True,
                width="stretch",
            )


if __name__ == "__main__":
    main()
