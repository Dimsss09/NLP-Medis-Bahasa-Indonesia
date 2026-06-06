"""Streamlit demo shell for Indonesian medical NER."""

from __future__ import annotations

import streamlit as st


def main() -> None:
    """Render the demo placeholder until the trained model is available."""
    st.set_page_config(page_title="Medical NER ID")
    st.title("Medical NER Bahasa Indonesia")
    st.info("Demo inferensi akan diaktifkan setelah model selesai dilatih.")
    st.text_area("Teks medis", "Pasien mengalami demam tinggi dan diberi paracetamol 500 mg.")


if __name__ == "__main__":
    main()
