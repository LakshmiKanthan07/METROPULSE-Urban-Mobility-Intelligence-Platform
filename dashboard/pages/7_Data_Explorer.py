"""
METROPULSE Dashboard — Page 7: Data Explorer
Enterprise Dark Command Center View
"""
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import streamlit as st
import pandas as pd

from dashboard.components.theme import apply_custom_css
from dashboard.components.sidebar import render_sidebar
from dashboard.components.header import render_header
from dashboard.components.section_header import render_section_header
from dashboard.components.metric_card import render_metric_card
from dashboard.components.data_table import render_data_table
from dashboard.components.empty_state import render_empty_state
from dashboard.components.data_loader import load, load_csv

st.set_page_config(page_title="Data Explorer | METROPULSE", page_icon="📁", layout="wide")
apply_custom_css()
render_sidebar()

DATASET_OPTIONS = {
    "Station Entries": ("tube_station_entries", "OBSERVED"),
    "Station Exits": ("tube_station_exits", "OBSERVED"),
    "Station Boarders": ("tube_station_boarders", "OBSERVED"),
    "Station Alighters": ("tube_station_alighters", "OBSERVED"),
    "Line Boarders": ("tube_line_boarders", "OBSERVED"),
    "Link Loads": ("tube_link_loads", "OBSERVED"),
    "Link Frequencies": ("tube_link_frequencies", "OBSERVED"),
    "Station Flows (Interchanges)": ("tube_station_flows", "OBSERVED"),
    "Link Congestion Analysis": ("congestion_link_congestion", "DERIVED"),
    "Service Adequacy Index": ("service_adequacy", "DERIVED"),
    "Station Clusters": ("ml_station_clusters", "DERIVED"),
    "Source Inventory": ("source_inventory", "OBSERVED"),
}

# ─── Sidebar Controls ────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("<div style='font-size: 11px; font-weight: 700; color: #94A3B8; text-transform: uppercase;'>Dataset Selection</div>", unsafe_allow_html=True)
    sel_name = st.selectbox("Choose Pipeline Table", list(DATASET_OPTIONS.keys()))
    dataset_key, lineage = DATASET_OPTIONS[sel_name]

# ─── Load Dataset ─────────────────────────────────────────────────────────────
if dataset_key in ["congestion_link_congestion", "service_adequacy", "ml_station_clusters", "source_inventory"]:
    if dataset_key == "source_inventory":
        from src.config.settings import REPORTS_DIR
        inv_path = REPORTS_DIR / "data_quality" / "source_inventory.csv"
        df = pd.read_csv(inv_path) if inv_path.exists() else pd.DataFrame()
    else:
        df = load_csv(dataset_key)
else:
    df = load(dataset_key)

render_header(
    page_name="Data Explorer & Export Hub",
    subtitle=f"Direct query, inspection, schema validation, and CSV export for {sel_name}",
    active_filters={"Table": sel_name, "Lineage": lineage},
)

if df.empty:
    render_empty_state(
        title=f"Dataset '{sel_name}' is Empty or Not Found",
        message="The parquet or CSV cache for this dataset has not been populated yet.",
        suggestion="Ensure the data pipeline has executed up to this stage.",
    )
    st.stop()

# ─── High Level Telemetry ─────────────────────────────────────────────────────
m1, m2, m3, m4 = st.columns(4)
with m1:
    render_metric_card(
        title="Total Records",
        value=len(df),
        unit="rows",
        subtitle="In-memory cache",
        status=lineage,
    )
with m2:
    render_metric_card(
        title="Schema Attributes",
        value=len(df.columns),
        unit="columns",
        subtitle="Feature count",
        status=lineage,
    )
with m3:
    mem_mb = df.memory_usage(deep=True).sum() / (1024 * 1024)
    render_metric_card(
        title="Memory Footprint",
        value=f"{mem_mb:.2f}",
        unit="MB",
        subtitle="PyArrow representation",
        status="DERIVED",
    )
with m4:
    null_cells = int(df.isna().sum().sum())
    render_metric_card(
        title="Null / Missing Cells",
        value=null_cells,
        unit="cells",
        subtitle=f"{null_cells / (len(df) * len(df.columns)) * 100:.1f}% of cells" if (len(df) * len(df.columns)) > 0 else "0%",
        status="OBSERVED",
    )

st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

# ─── Filtering controls ───────────────────────────────────────────────────────
render_section_header(
    title=f"Query & Filter: {sel_name}",
    subtitle="Apply faceted filters or regex keyword queries across table records.",
    status=lineage,
)

col_f1, col_f2, col_f3 = st.columns(3)
filtered = df.copy()

with col_f1:
    if "year" in filtered.columns:
        yrs = sorted(filtered["year"].dropna().unique().tolist())
        sel_yrs = st.multiselect("Filter Years", yrs, default=yrs)
        if sel_yrs:
            filtered = filtered[filtered["year"].isin(sel_yrs)]

with col_f2:
    if "day_type" in filtered.columns:
        days = sorted(filtered["day_type"].dropna().unique().tolist())
        sel_days = st.multiselect("Filter Day Types", days, default=days)
        if sel_days:
            filtered = filtered[filtered["day_type"].isin(sel_days)]

with col_f3:
    if "line" in filtered.columns:
        lines = sorted(filtered["line"].dropna().unique().tolist())
        sel_lines = st.multiselect("Filter Lines", lines, default=[])
        if sel_lines:
            filtered = filtered[filtered["line"].isin(sel_lines)]
    elif "line_name" in filtered.columns:
        lines = sorted(filtered["line_name"].dropna().unique().tolist())
        sel_lines = st.multiselect("Filter Lines", lines, default=[])
        if sel_lines:
            filtered = filtered[filtered["line_name"].isin(sel_lines)]

search = st.text_input("🔍 Search within records (regex or text query)", "")
if search:
    mask = filtered.astype(str).apply(lambda row: row.str.contains(search, case=False).any(), axis=1)
    filtered = filtered[mask]

# Data table presentation
render_data_table(
    df=filtered,
    title=f"Query Results: {len(filtered):,} Matching Records",
    download_filename=f"{dataset_key}_export.csv",
    max_rows=100,
)
