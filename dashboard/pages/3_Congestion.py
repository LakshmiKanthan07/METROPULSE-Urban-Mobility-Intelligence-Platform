"""
METROPULSE Dashboard — Page 3: Congestion Intelligence
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
    load, load_csv, LINE_COLOURS, format_number, PLOTLY_TEMPLATE
)

st.set_page_config(page_title="Congestion Intelligence | METROPULSE", page_icon="🔥", layout="wide")
st.markdown("""<style>.stApp{background:#0a0f1e;color:#f1f5f9;}[data-testid="stSidebar"]{background:#111827!important;}
[data-testid="metric-container"]{background:#1a2235;border:1px solid #1e3a5f;border-radius:12px;padding:1rem!important;}
[data-testid="metric-container"] [data-testid="stMetricValue"]{color:#ef4444!important;font-size:1.8rem!important;font-weight:700;}
h1,h2,h3{color:#f1f5f9!important;}</style>""", unsafe_allow_html=True)

st.markdown("# 🔥 Congestion Intelligence")
st.markdown("**Passenger load per train, link-level bottlenecks, and congestion risk classification**")

# ─── Load data ────────────────────────────────────────────────────────────────
link_cong = load_csv("congestion_link_congestion")
st_cong   = load_csv("congestion_station_congestion")
service_adeq = load_csv("service_adequacy")
peak_prof = load_csv("congestion_peak_profile")

if link_cong.empty:
    st.info("⚠️ Congestion analytics data is being processed or not yet generated. Please run `python run.py --stage analytics`.")
    st.stop()

# ─── Sidebar filters ─────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("**Filters**")
    all_years = sorted(link_cong["year"].dropna().unique()) if "year" in link_cong.columns else [2024]
    sel_year  = st.selectbox("Year", all_years, index=len(all_years)-1)
    all_days  = sorted(link_cong["day_type"].dropna().unique()) if "day_type" in link_cong.columns else ["MON"]
    sel_day   = st.selectbox("Day Type", all_days, index=0)
    all_lines = ["All Lines"] + sorted(link_cong["line"].dropna().unique().tolist()) if "line" in link_cong.columns else ["All Lines"]
    sel_line  = st.selectbox("Line", all_lines, index=0)

# Filter
filtered_links = link_cong[(link_cong["year"] == sel_year) & (link_cong["day_type"] == sel_day)].copy()
if sel_line != "All Lines":
    filtered_links = filtered_links[filtered_links["line"] == sel_line]

# ─── KPI Metrics ──────────────────────────────────────────────────────────────
col1, col2, col3, col4, col5 = st.columns(5)
crit_links = (filtered_links["congestion_class"] == "Critical").sum() if "congestion_class" in filtered_links.columns else 0
high_links = (filtered_links["congestion_class"] == "High").sum() if "congestion_class" in filtered_links.columns else 0
max_ppt    = filtered_links["pax_per_train_am_peak"].max() if "pax_per_train_am_peak" in filtered_links.columns else 0
avg_ppt    = filtered_links["pax_per_train_am_peak"].mean() if "pax_per_train_am_peak" in filtered_links.columns else 0
crit_stns  = (st_cong["station_congestion_class"] == "Critical").sum() if not st_cong.empty and "station_congestion_class" in st_cong.columns else 0

col1.metric("🔴 Critical Links", f"{crit_links}")
col2.metric("🟠 High Congestion Links", f"{high_links}")
col3.metric("🚂 Peak Load / Train", f"{max_ppt:,.0f} pax" if not pd.isna(max_ppt) else "N/A")
col4.metric("📊 Avg AM Load / Train", f"{avg_ppt:,.0f} pax" if not pd.isna(avg_ppt) else "N/A")
col5.metric("🚨 Congested Stations", f"{crit_stns}")

st.markdown("---")

tabs = st.tabs(["🚇 Link-Level Congestion", "📊 Load Per Train Distribution", "🏛️ Station Bottlenecks", "⏰ Peak Windows"])

with tabs[0]:
    c1, c2 = st.columns([3, 2])
    with c1:
        st.markdown("### Top 20 Most Congested Track Links (AM Peak)")
        top_links = (
            filtered_links.sort_values("pax_per_train_am_peak", ascending=False)
            .head(20)
            .copy()
        )
        top_links["segment"] = top_links["from_station"] + " → " + top_links["to_station"] + " (" + top_links["direction"] + ")"
        
        fig = px.bar(
            top_links.sort_values("pax_per_train_am_peak", ascending=True),
            x="pax_per_train_am_peak", y="segment",
            color="congestion_class",
            color_discrete_map={"Critical": "#ef4444", "High": "#f59e0b", "Moderate": "#3b82f6", "Low": "#10b981"},
            orientation="h",
            labels={"pax_per_train_am_peak": "Pax Per Train (AM Peak)", "segment": "Link Segment"},
            hover_data=["line", "am_peak", "freq_am_peak"]
        )
        fig.update_layout(**PLOTLY_TEMPLATE["layout"], height=600, margin=dict(l=0, r=20, t=10, b=40))
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.markdown("### Congestion Risk Breakdown")
        if "congestion_class" in filtered_links.columns:
            class_counts = filtered_links["congestion_class"].value_counts().reset_index()
            class_counts.columns = ["Class", "Count"]
            fig_pie = px.pie(
                class_counts, values="Count", names="Class",
                color="Class",
                color_discrete_map={"Critical": "#ef4444", "High": "#f59e0b", "Moderate": "#3b82f6", "Low": "#10b981"},
                hole=0.45
            )
            fig_pie.update_layout(**PLOTLY_TEMPLATE["layout"], height=350, margin=dict(l=10, r=10, t=20, b=20))
            st.plotly_chart(fig_pie, use_container_width=True)

        st.markdown("### Line Congestion Comparison")
        line_summary = (
            filtered_links.groupby("line")["pax_per_train_am_peak"]
            .mean().reset_index().sort_values("pax_per_train_am_peak", ascending=False)
        )
        fig_ln = px.bar(
            line_summary, x="line", y="pax_per_train_am_peak",
            color="line",
            color_discrete_map=LINE_COLOURS,
            labels={"pax_per_train_am_peak": "Mean AM Pax/Train", "line": "Line"}
        )
        fig_ln.update_layout(**PLOTLY_TEMPLATE["layout"], showlegend=False, height=250, xaxis_tickangle=-30, margin=dict(l=0, r=0, t=10, b=60))
        st.plotly_chart(fig_ln, use_container_width=True)

with tabs[1]:
    st.markdown("### Passenger Load Per Train: AM Peak vs PM Peak vs Midday")
    col_p1, col_p2 = st.columns(2)
    with col_p1:
        fig_scatter = px.scatter(
            filtered_links,
            x="freq_am_peak", y="am_peak",
            color="congestion_class",
            size="pax_per_train_am_peak",
            hover_name="link",
            color_discrete_map={"Critical": "#ef4444", "High": "#f59e0b", "Moderate": "#3b82f6", "Low": "#10b981"},
            labels={"freq_am_peak": "Train Frequency (Trains in AM Peak)", "am_peak": "Total AM Passengers"},
            title="Service vs Demand (AM Peak)"
        )
        fig_scatter.update_layout(**PLOTLY_TEMPLATE["layout"], height=450)
        st.plotly_chart(fig_scatter, use_container_width=True)

    with col_p2:
        fig_hist = px.histogram(
            filtered_links,
            x="pax_per_train_am_peak",
            nbins=30,
            color="congestion_class",
            color_discrete_map={"Critical": "#ef4444", "High": "#f59e0b", "Moderate": "#3b82f6", "Low": "#10b981"},
            labels={"pax_per_train_am_peak": "Pax Per Train"},
            title="Distribution of Load Per Train (AM Peak)"
        )
        fig_hist.update_layout(**PLOTLY_TEMPLATE["layout"], height=450)
        st.plotly_chart(fig_hist, use_container_width=True)

with tabs[2]:
    st.markdown("### Station-Level Passenger Congestion")
    if not st_cong.empty:
        st_sub = st_cong[(st_cong["year"] == sel_year) & (st_cong["day_type"] == sel_day)].copy()
        if not st_sub.empty:
            top_st_cong = st_sub.sort_values("am_peak", ascending=False).head(25)
            fig_st = px.bar(
                top_st_cong,
                x="station", y=["am_peak", "pm_peak"],
                barmode="group",
                color_discrete_sequence=["#ef4444", "#f59e0b"],
                labels={"value": "Entries", "station": "Station", "variable": "Peak Window"}
            )
            fig_st.update_layout(**PLOTLY_TEMPLATE["layout"], height=450, xaxis_tickangle=-45)
            st.plotly_chart(fig_st, use_container_width=True)

with tabs[3]:
    st.markdown("### Peak Congestion Temporal Windows")
    if not peak_prof.empty:
        pk_sub = peak_prof[(peak_prof["year"] == sel_year) & (peak_prof["day_type"] == sel_day)].copy()
        if not pk_sub.empty:
            fig_pk = px.line(
                pk_sub, x="time_interval", y=["passengers", "rolling_avg"],
                labels={"value": "Total Passengers", "time_interval": "15-Min Interval"},
                color_discrete_sequence=["#3b82f6", "#ef4444"],
                title="System-Wide Passenger Flow Profile with Rolling 1-Hour Trend"
            )
            fig_pk.update_layout(**PLOTLY_TEMPLATE["layout"], height=450, xaxis_tickangle=45)
            st.plotly_chart(fig_pk, use_container_width=True)

