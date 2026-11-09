"""
METROPULSE Dashboard — Page 4: Geospatial Intelligence
"""
import sys
from pathlib import Path
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

ROOT = Path(__file__).parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from dashboard.components.data_loader import (
    load, load_csv, load_coords, LINE_COLOURS, format_number, PLOTLY_TEMPLATE
)

st.set_page_config(page_title="Geospatial Intelligence | METROPULSE", page_icon="🗺️", layout="wide")
st.markdown("""<style>.stApp{background:#0a0f1e;color:#f1f5f9;}[data-testid="stSidebar"]{background:#111827!important;}
[data-testid="metric-container"]{background:#1a2235;border:1px solid #1e3a5f;border-radius:12px;padding:1rem!important;}
[data-testid="metric-container"] [data-testid="stMetricValue"]{color:#06b6d4!important;font-size:1.8rem!important;font-weight:700;}
h1,h2,h3{color:#f1f5f9!important;}</style>""", unsafe_allow_html=True)

st.markdown("# 🗺️ Geospatial Intelligence")
st.markdown("**Spatial distribution of passenger demand, network connectivity, and accessibility across Greater London**")

# ─── Load data ────────────────────────────────────────────────────────────────
coords = load_coords()
entries = load("tube_station_entries")
link_cong = load_csv("congestion_link_congestion")
clusters = load_csv("ml_station_clusters")
accessibility = load_csv("spatial_station_accessibility")

if coords.empty:
    from src.geospatial.station_mapping import fetch_station_coordinates
    coords = fetch_station_coordinates()

# Merge coords with entries
if not entries.empty:
    st_agg = entries.groupby("asc")[["total", "am_peak", "pm_peak"]].mean().reset_index()
    geo_df = coords.merge(st_agg, on="asc", how="left").fillna({"total": 0, "am_peak": 0, "pm_peak": 0})
else:
    geo_df = coords.copy()
    geo_df["total"] = 5000

# Merge cluster labels if available
if not clusters.empty and "asc" in clusters.columns:
    geo_df = geo_df.merge(clusters[["asc", "cluster_label"]].drop_duplicates(subset=["asc"]), on="asc", how="left")
    geo_df["cluster_label"] = geo_df["cluster_label"].fillna("Unclassified")
else:
    geo_df["cluster_label"] = "Standard Station"

# Merge accessibility if available
if not accessibility.empty and "asc" in accessibility.columns:
    geo_df = geo_df.merge(accessibility[["asc", "nearest_station_km", "dist_to_centre_km"]].drop_duplicates(subset=["asc"]), on="asc", how="left")

# ─── Sidebar ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("**Map Controls**")
    metric_choice = st.selectbox("Sizing Metric", ["Total Daily Entries", "AM Peak Entries", "PM Peak Entries"])
    metric_col = "total" if metric_choice == "Total Daily Entries" else "am_peak" if metric_choice == "AM Peak Entries" else "pm_peak"
    colour_by = st.selectbox("Colour By", ["Demand Intensity", "Cluster Type", "Fare Zone"])

# ─── KPI Metrics ──────────────────────────────────────────────────────────────
k1, k2, k3, k4 = st.columns(4)
k1.metric("Mapped Stations", f"{len(geo_df)}")
k2.metric("Inner London (Zone 1-2)", f"{(geo_df['fare_zone'].isin(['1', '1/2', '2', '2/3'])).sum()}" if "fare_zone" in geo_df.columns else "N/A")
k3.metric("Outer London (Zone 3-6)", f"{(geo_df['fare_zone'].isin(['3', '4', '5', '6'])).sum()}" if "fare_zone" in geo_df.columns else "N/A")
avg_dist = geo_df['dist_to_centre_km'].mean() if 'dist_to_centre_km' in geo_df.columns else 8.5
k4.metric("Avg Distance to Centre", f"{avg_dist:.1f} km" if not pd.isna(avg_dist) else "N/A")

st.markdown("---")

# ─── Map Visualization ───────────────────────────────────────────────────────
st.markdown("### Interactive London Underground Network Map")

color_arg = metric_col
if colour_by == "Cluster Type":
    color_arg = "cluster_label"
elif colour_by == "Fare Zone":
    color_arg = "fare_zone"

hover_data_list = ["station", "fare_zone", "total", "am_peak", "cluster_label"]
hover_data_list = [c for c in hover_data_list if c in geo_df.columns]

fig_map = px.scatter_mapbox(
    geo_df,
    lat="lat", lon="lon",
    size=metric_col,
    color=color_arg,
    size_max=22,
    zoom=10.2,
    center=dict(lat=51.5074, lon=-0.1278),
    mapbox_style="carto-darkmatter",
    hover_name="station",
    hover_data=hover_data_list,
    title=f"London Underground Stations — {metric_choice}",
    color_continuous_scale=px.colors.sequential.Tealgrn if colour_by == "Demand Intensity" else None
)
fig_map.update_layout(
    **PLOTLY_TEMPLATE["layout"],
    height=600,
    margin=dict(l=0, r=0, t=30, b=0),
)
st.plotly_chart(fig_map, use_container_width=True)

# ─── Geospatial Distributions ────────────────────────────────────────────────
col_g1, col_g2 = st.columns(2)
with col_g1:
    st.markdown("### Passenger Demand by Fare Zone")
    if "fare_zone" in geo_df.columns and "total" in geo_df.columns:
        zone_demand = geo_df.groupby("fare_zone")["total"].agg(["sum", "mean", "count"]).reset_index()
        fig_zone = px.bar(
            zone_demand.sort_values("sum", ascending=False),
            x="fare_zone", y="sum",
            color="mean",
            labels={"fare_zone": "Fare Zone", "sum": "Total Daily Entries", "mean": "Avg / Station"},
            color_continuous_scale="Viridis",
            title="Total and Mean Station Demand by Fare Zone"
        )
        fig_zone.update_layout(**PLOTLY_TEMPLATE["layout"], height=380)
        st.plotly_chart(fig_zone, use_container_width=True)

with col_g2:
    st.markdown("### Demand Decay with Distance from Central London")
    if "dist_to_centre_km" in geo_df.columns:
        fig_decay = px.scatter(
            geo_df.dropna(subset=["dist_to_centre_km", "total"]),
            x="dist_to_centre_km", y="total",
            color="fare_zone" if "fare_zone" in geo_df.columns else None,
            hover_name="station",
            trendline="lowess",
            labels={"dist_to_centre_km": "Distance to Charing Cross (km)", "total": "Daily Station Entries"},
            title="Station Demand Decay Gradient"
        )
        fig_decay.update_layout(**PLOTLY_TEMPLATE["layout"], height=380)
        st.plotly_chart(fig_decay, use_container_width=True)

