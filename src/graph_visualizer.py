"""Visualizes NetworkX graphs using PyVis with custom medical branding styling."""

from __future__ import annotations

import networkx as nx
from pyvis.network import Network

# Color scheme matching the demo brand
LABEL_COLORS = {
    "GEJALA": "#be123c",     # Crimson
    "DIAGNOSIS": "#a16207",  # Yellowish Brown
    "OBAT": "#1d4ed8",       # Blue
    "DOSIS": "#15803d",      # Green
    "ANATOMI": "#6d28d9",    # Purple
}


def generate_graph_html(G: nx.DiGraph, height: str = "450px", width: str = "100%") -> str:
    """Generate Vis.js interactive physics network HTML from NetworkX DiGraph.
    
    Returns:
        HTML string of the network visualization
    """
    if len(G) == 0:
        return "<div style='color:#94a3b8; text-align:center; padding:2rem;'>Graf kosong. Tidak ada entitas atau hubungan yang dapat divisualisasikan.</div>"

    # Initialize PyVis network
    # We use directed=True to show arrowheads from head to tail
    net = Network(
        height=height,
        width=width,
        directed=True,
        notebook=False,
        bgcolor="#0f172a",      # Slate 900 background
        font_color="#e2e8f0"    # Slate 200 text
    )

    # Set VisJS physics configuration for a clean layout
    # BarnesHut is robust and handles 10-100 nodes very well
    net.barnes_hut(
        gravity=-2200,
        central_gravity=0.15,
        spring_length=120,
        spring_strength=0.08,
        damping=0.96
    )

    # Map relationship types to user-friendly titles
    rel_names = {
        "dosage_of": "Dosis Dari 💊",
        "treats": "Mengobati 🩺",
        "located_in": "Lokasi di 📍"
    }

    # Add Nodes
    for node, attrs in G.nodes(data=True):
        label_type = attrs.get("label", "Unknown")
        color = LABEL_COLORS.get(label_type, "#64748b")
        
        std_name = attrs.get("standard_name", node)
        std_code = attrs.get("standard_code")
        
        # Tooltip content shown on hover
        tooltip_lines = [
            f"Teks: <b>{std_name}</b>",
            f"Kategori: <b>{label_type}</b>"
        ]
        if std_code:
            tooltip_lines.append(f"Standardisasi: <b>{std_code}</b>")
        tooltip_html = "<br>".join(tooltip_lines)

        # Main display label shown on the node
        display_label = std_name
        if std_code:
            display_label += f"\n({std_code.split(': ')[-1]})"

        # Node size based on importance
        node_size = 25 if label_type in {"OBAT", "GEJALA", "DIAGNOSIS"} else 18

        net.add_node(
            node,
            label=display_label,
            title=tooltip_html,
            color=color,
            size=node_size,
            shape="dot",
            borderWidth=1.5,
            borderWidthSelected=3.0
        )

    # Add Edges
    for u, v, attrs in G.edges(data=True):
        rel_type = attrs.get("type", "")
        edge_label = rel_names.get(rel_type, rel_type)
        
        net.add_edge(
            u,
            v,
            label=edge_label,
            color="#64748b",      # Slate 500
            width=2,
            font={"size": 10, "color": "#cbd5e1", "strokeWidth": 0}
        )

    # Generate HTML content
    # vis.js scripts are fetched from CDN
    html_content = net.generate_html()
    
    # Injected styling to vis-network canvas so it integrates cleanly in Streamlit iframe
    custom_style = """
        body { margin: 0; padding: 0; background-color: #0f172a; overflow: hidden; }
        #mynetwork {
            width: 100% !important;
            height: 100% !important;
            background-color: #0f172a !important;
            border: 1px solid #1e293b !important;
        }
    """
    for style_tag in ['<style type="text/css">', "<style type=\"text/css\">", '<style type=\'text/css\'>']:
        if style_tag in html_content:
            html_content = html_content.replace(style_tag, f'{style_tag}\n{custom_style}')
            break
            
    return html_content
