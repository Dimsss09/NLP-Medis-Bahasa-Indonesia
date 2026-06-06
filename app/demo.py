"""Interactive Streamlit demo for Indonesian medical NER."""

from __future__ import annotations

import html
import sys
from pathlib import Path

import streamlit as st

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.predict import DEFAULT_MODEL_DIR, EntitySpan, load_model, predict_entities


LABEL_COLORS = {
    "GEJALA": ("#fff1f2", "#be123c"),
    "OBAT": ("#eff6ff", "#1d4ed8"),
    "DOSIS": ("#f0fdf4", "#15803d"),
    "DIAGNOSIS": ("#fefce8", "#a16207"),
    "ANATOMI": ("#f5f3ff", "#6d28d9"),
}


@st.cache_resource(show_spinner="Memuat model NER...")
def cached_model(model_dir: str):
    """Load model once per Streamlit session."""
    return load_model(Path(model_dir))


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
            "<mark style=\""
            f"background:{background}; color:{color}; "
            "padding:0.15rem 0.35rem; border-radius:0.35rem; "
            "font-weight:600; line-height:2;\">"
            f"{html.escape(text[entity.start:entity.end])}"
            f"<span style=\"font-size:0.72rem; margin-left:0.35rem;\">{html.escape(entity.label)}</span>"
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
    st.title("Medical NER Bahasa Indonesia")

    model_dir = st.sidebar.text_input("Model directory", str(DEFAULT_MODEL_DIR))
    st.sidebar.caption("Model lokal hasil fine-tuning Fase 3.")

    sample_text = "Pasien mengalami demam tinggi, nyeri dada, dan minum paracetamol 500 mg sesudah makan."
    text = st.text_area("Teks medis", sample_text, height=140)

    tokenizer, model, device = cached_model(model_dir)
    if st.button("Ekstrak Entitas", type="primary") or text:
        token_predictions, entities = predict_entities(text, tokenizer, model, device)
        highlighted = render_highlighted_text(text, entities)

        st.subheader("Hasil Sorotan")
        st.markdown(
            f"<div style='font-size:1.05rem; line-height:2.1; padding:1rem 0;'>{highlighted}</div>",
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
