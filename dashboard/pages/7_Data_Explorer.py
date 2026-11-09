"""
METROPULSE Dashboard — Page 7: Data Explorer
"""
import sys
from pathlib import Path
import streamlit as st
import pandas as pd

ROOT = Path(__file__).parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from dashboard.components.data_loader import (
    load, load_csv, format_number
)

st.set_page_config(page_title="Data Explorer | METROPULSE", page_icon="📁", layout="wide")
st.markdown("""<style>.stApp{background:#0a0f1e;color:#f1f5f9;}[data-testid="stSidebar"]{background:#111827!important;}
[data-testid="metric-container"]{background:#1a2235;border:1px solid #1e3a5f;border-radius:12px;padding:1rem!important;}
[data-testid="metric-container"] [data-testid="stMetricValue"]{color:#3b82f6!important;font-size:1.8rem!important;font-weight:700;}
h1,h2,h3{color:#f1f5f9!important;}</style>""", unsafe_allow_html=True)

st.markdown("# 📁 Data Explorer & Export Hub")
st.markdown("**Inspect, filter, query, and download processed TfL London Underground datasets**")

DATASET_OPTIONS = {
    "Station Entries": "tube_station_entries",
    "Station Exits": "tube_station_exits",
    "Station Boarders": "tube_station_boarders",
    "Station Alighters": "tube_station_alighters",
    "Line Boarders": "tube_line_boarders",
    "Link Loads": "tube_link_loads",
    "Link Frequencies": "tube_link_frequencies",
    "Station Flows (Interchanges)": "tube_station_flows",
    "Link Congestion Analysis": "congestion_link_congestion",
    "Service Adequacy Index": "service_adequacy",
    "Station Clusters": "ml_station_clusters",
    "Source Inventory": "source_inventory"
}

# ─── Sidebar Controls ────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("**Dataset Selection**")
    sel_name = st.selectbox("Choose Table", list(DATASET_OPTIONS.keys()))
    dataset_key = DATASET_OPTIONS[sel_name]

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

if df.empty:
    st.warning(f"Dataset `{sel_name}` ({dataset_key}) has not been populated yet. Please run the pipeline.")
    st.stop()

# ─── Filtering controls ───────────────────────────────────────────────────────
st.markdown(f"### Active Table: `{sel_name}` ({len(df):,} total records)")

col_f1, col_f2, col_f3 = st.columns(3)
filtered = df.copy()

with col_f1:
    if "year" in filtered.columns:
        yrs = sorted(filtered["year"].dropna().unique())
        sel_yrs = st.multiselect("Filter Years", yrs, default=yrs)
        if sel_yrs:
            filtered = filtered[filtered["year"].isin(sel_yrs)]

with col_f2:
    if "day_type" in filtered.columns:
        days = sorted(filtered["day_type"].dropna().unique())
        sel_days = st.multiselect("Filter Day Types", days, default=days)
        if sel_days:
            filtered = filtered[filtered["day_type"].isin(sel_days)]

with col_f3:
    if "line" in filtered.columns:
        lines = sorted(filtered["line"].dropna().unique())
        sel_lines = st.multiselect("Filter Lines", lines, default=[])
        if sel_lines:
            filtered = filtered[filtered["line"].isin(sel_lines)]
    elif "line_name" in filtered.columns:
        lines = sorted(filtered["line_name"].dropna().unique())
        sel_lines = st.multiselect("Filter Lines", lines, default=[])
        if sel_lines:
            filtered = filtered[filtered["line_name"].isin(sel_lines)]

# Search box
search = st.text_input("🔍 Search within records (regex or text)", "")
if search:
    mask = filtered.astype(str).apply(lambda row: row.str.contains(search, case=False).any(), axis=1)
    filtered = filtered[mask]

st.markdown(f"**Displaying {len(filtered):,} matching records** (previewing up to 1,000 rows):")
st.dataframe(filtered.head(1000), use_container_width=True, height=450)

# Export button
csv_data = filtered.head(50000).to_csv(index=False).encode('utf-8')
st.download_button(
    label=f"⬇️ Download Filtered Data as CSV ({len(filtered):,} rows)",
    data=csv_data,
    file_name=f"{dataset_key}_filtered.csv",
    mime="text/csv"
)

