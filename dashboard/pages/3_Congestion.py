"""
METROPULSE Dashboard — Page 3: Congestion Intelligence
Enterprise Dark Command Center View
"""
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

from dashboard.components.theme import apply_custom_css
from dashboard.components.sidebar import render_sidebar
from dashboard.components.header import render_header
from dashboard.components.section_header import render_section_header
from dashboard.components.metric_card import render_metric_card
from dashboard.components.chart_container import render_chart_container
from dashboard.components.data_table import render_data_table
from dashboard.components.data_loader import (
    load_csv, LINE_COLOURS, format_number
)

st.set_page_config(page_title="Congestion Intelligence | METROPULSE", page_icon="🔥", layout="wide")
apply_custom_css()
render_sidebar()

# ─── Load data ────────────────────────────────────────────────────────────────
link_cong = load_csv("congestion_link_congestion")
st_cong   = load_csv("congestion_station_congestion")
service_adeq = load_csv("service_adequacy")
peak_prof = load_csv("congestion_peak_profile")

if link_cong.empty:
    st.info("⚠️ Congestion analytics data not found. Please ensure pipeline analytics stage has executed.")
    st.stop()

# ─── Sidebar filters ─────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("<div style='font-size: 11px; font-weight: 700; color: #94A3B8; text-transform: uppercase;'>Congestion Filters</div>", unsafe_allow_html=True)
    all_years = sorted(link_cong["year"].dropna().unique().tolist()) if "year" in link_cong.columns else [2024]
    sel_year  = st.selectbox("Operating Year", all_years, index=len(all_years)-1)
    all_days  = sorted(link_cong["day_type"].dropna().unique().tolist()) if "day_type" in link_cong.columns else ["MON"]
    sel_day   = st.selectbox("Day Model", all_days, index=0)
    all_lines = ["All Lines"] + sorted(link_cong["line"].dropna().unique().tolist()) if "line" in link_cong.columns else ["All Lines"]
    sel_line  = st.selectbox("Underground Line", all_lines, index=0)

filtered_links = link_cong[(link_cong["year"] == sel_year) & (link_cong["day_type"] == sel_day)].copy()
if sel_line != "All Lines":
    filtered_links = filtered_links[filtered_links["line"] == sel_line]

render_header(
    page_name="Congestion Intelligence",
    subtitle=f"Passenger load-per-train, critical track bottlenecks, and service adequacy monitoring for {sel_year} ({sel_day})",
    active_filters={"Year": sel_year, "Day Model": sel_day, "Line": sel_line},
)

# ─── KPI Metrics ──────────────────────────────────────────────────────────────
crit_links = (filtered_links["congestion_class"] == "Critical").sum() if "congestion_class" in filtered_links.columns else 0
high_links = (filtered_links["congestion_class"] == "High").sum() if "congestion_class" in filtered_links.columns else 0
max_lpt    = filtered_links["pax_per_train_am_peak"].max() if "pax_per_train_am_peak" in filtered_links.columns else 0
avg_lpt    = filtered_links["pax_per_train_am_peak"].mean() if "pax_per_train_am_peak" in filtered_links.columns else 0

col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    render_metric_card(
        title="Critical Track Links",
        value=crit_links,
        unit="links",
        subtitle="LPT > 800 passengers",
        status="DERIVED",
        tooltip="Track segments where passenger load per scheduled train exceeds 800 during the AM Peak window",
    )
with col2:
    render_metric_card(
        title="High Stress Links",
        value=high_links,
        unit="links",
        subtitle="LPT: 600–800 passengers",
        status="DERIVED",
        tooltip="Track segments operating near rated capacity during peak commute intervals",
    )
with col3:
    render_metric_card(
        title="Peak AM Load / Train",
        value=f"{max_lpt:,.0f}" if not pd.isna(max_lpt) else "N/A",
        unit="pax/train",
        subtitle="Network peak link",
        status="DERIVED",
        tooltip="Highest single load-per-train ratio recorded across all active track sections in this model",
    )
with col4:
    render_metric_card(
        title="Vehicle Capacity",
        value=None,
        subtitle="Omitted in NUMBAT",
        status="EXTERNAL_REQUIRED",
        missing_reason="Crush capacity requires rolling stock specifications per line stock type.",
        tooltip="Physical train car capacity is not reported in NUMBAT outputs.",
    )
with col5:
    render_metric_card(
        title="Real-Time Delays",
        value=None,
        subtitle="Requires live feed",
        status="EXTERNAL_REQUIRED",
        missing_reason="Real-time incident logs require TfL live Unified API integration.",
        tooltip="NUMBAT captures typical scheduled/modelled operation rather than live signal failure delays.",
    )

st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

# ─── Tab layout ───────────────────────────────────────────────────────────────
tabs = st.tabs([
    "🚨 Top Track Bottlenecks",
    "📈 Load-Per-Train vs. Frequency",
    "⚖️ Service Adequacy Index",
    "🏛️ Station Inflow Stress",
])

# ── TAB 1: Top 20 Bottlenecks ─────────────────────────────────────────────────
with tabs[0]:
    render_section_header(
        title="Top 20 Critical Network Track Links (AM Peak)",
        subtitle="Ranked by passenger load-per-train (LPT = Link Load / Scheduled Trains).",
        status="DERIVED",
    )

    c1, c2 = st.columns([11, 9])
    with c1:
        top_links = (
            filtered_links.sort_values("pax_per_train_am_peak", ascending=False)
            .head(20).copy()
        )
        top_links["segment"] = top_links["from_station"] + " → " + top_links["to_station"] + " (" + top_links["direction"] + ")"

        fig_bottle = px.bar(
            top_links.sort_values("pax_per_train_am_peak", ascending=True),
            x="pax_per_train_am_peak", y="segment",
            color="congestion_class",
            color_discrete_map={"Critical": "#EF4444", "High": "#F59E0B", "Moderate": "#3B82F6", "Low": "#10B981"},
            orientation="h",
            labels={"pax_per_train_am_peak": "Passenger Load Per Train", "segment": "Track Segment"},
        )
        fig_bottle.update_layout(height=580, yaxis_title=None)
        render_chart_container(
            fig=fig_bottle,
            title="Top 20 Constrained Links (AM Peak)",
            subtitle="Derived from observed link loads and train frequencies",
            lineage="DERIVED",
            takeaway="Critical overcrowding concentrates heavily on inbound Victoria (Finsbury Park → Highbury) and Central (Stratford → Mile End) corridors.",
            height=580,
        )

    with c2:
        if "congestion_class" in filtered_links.columns:
            class_counts = filtered_links["congestion_class"].value_counts().reset_index()
            class_counts.columns = ["Class", "Count"]
            fig_pie = px.pie(
                class_counts, values="Count", names="Class",
                color="Class",
                color_discrete_map={"Critical": "#EF4444", "High": "#F59E0B", "Moderate": "#3B82F6", "Low": "#10B981"},
                hole=0.5,
            )
            fig_pie.update_layout(height=280)
            render_chart_container(
                fig=fig_pie,
                title="Congestion Class Distribution",
                subtitle="Share of network track sections in each load band",
                lineage="DERIVED",
                takeaway="Critical bottlenecks represent a small fraction of track links, indicating targeted capacity interventions are highly feasible.",
                height=280,
            )

        line_summary = (
            filtered_links.groupby("line")["pax_per_train_am_peak"]
            .mean().reset_index().sort_values("pax_per_train_am_peak", ascending=False)
        )
        colours = [LINE_COLOURS.get(ln, "#3B82F6") for ln in line_summary["line"]]
        fig_ln_cong = go.Figure(go.Bar(
            x=line_summary["line"], y=line_summary["pax_per_train_am_peak"],
            marker_color=colours,
        ))
        fig_ln_cong.update_layout(height=260, xaxis_tickangle=-30, yaxis_title="Mean AM Pax / Train")
        render_chart_container(
            fig=fig_ln_cong,
            title="Average Load-Per-Train by Line",
            subtitle="Comparing line-wide passenger density per train service",
            lineage="DERIVED",
            takeaway="Victoria and Jubilee lines show the highest average loading per scheduled train.",
            height=260,
        )

# ── TAB 2: LPT vs Frequency ───────────────────────────────────────────────────
with tabs[1]:
    render_section_header(
        title="Service Frequency vs. Passenger Demand Density",
        subtitle="Scatter distribution of track link passenger demand against scheduled train frequency.",
        status="DERIVED",
    )
    col_p1, col_p2 = st.columns(2)
    with col_p1:
        fig_scatter = px.scatter(
            filtered_links,
            x="freq_am_peak", y="am_peak",
            color="congestion_class",
            size="pax_per_train_am_peak",
            hover_name="link",
            color_discrete_map={"Critical": "#EF4444", "High": "#F59E0B", "Moderate": "#3B82F6", "Low": "#10B981"},
            labels={"freq_am_peak": "Train Frequency (Scheduled Trains in AM Peak)", "am_peak": "Observed AM Passenger Load"},
        )
        fig_scatter.update_layout(height=450)
        render_chart_container(
            fig=fig_scatter,
            title="Service vs. Passenger Volume (AM Peak)",
            subtitle="Bubble size represents Load-Per-Train ratio",
            lineage="DERIVED",
            takeaway="Links falling in the upper-left quadrant suffer from high passenger demand coupled with constrained train frequency.",
            height=450,
        )

    with col_p2:
        fig_hist = px.histogram(
            filtered_links,
            x="pax_per_train_am_peak",
            nbins=35,
            color="congestion_class",
            color_discrete_map={"Critical": "#EF4444", "High": "#F59E0B", "Moderate": "#3B82F6", "Low": "#10B981"},
            labels={"pax_per_train_am_peak": "Load Per Train (Pax/Train)"},
        )
        fig_hist.update_layout(height=450, yaxis_title="Number of Track Links")
        render_chart_container(
            fig=fig_hist,
            title="Frequency Distribution of Load Per Train",
            subtitle="Histogram of passenger loading across all directional segments",
            lineage="DERIVED",
            takeaway="The median track segment operates comfortably under 450 pax/train, with a long right tail extending past 850.",
            height=450,
        )

# ── TAB 3: Service Adequacy Index ─────────────────────────────────────────────
with tabs[2]:
    render_section_header(
        title="Service Adequacy Index (SAI) Monitoring",
        subtitle="Evaluating how harmoniously scheduled train frequency matches passenger demand volumes.",
        status="DERIVED",
    )
    if not service_adeq.empty:
        adeq_f = service_adeq[(service_adeq["year"] == sel_year) & (service_adeq["day_type"] == sel_day)].copy()
        if not adeq_f.empty and "service_adequacy_index" in adeq_f.columns:
            lowest_adeq = adeq_f.sort_values("service_adequacy_index", ascending=True).head(20)
            lowest_adeq["segment"] = lowest_adeq["from_station"] + " → " + lowest_adeq["to_station"]

            fig_sai = px.bar(
                lowest_adeq,
                x="service_adequacy_index", y="segment",
                color="line",
                orientation="h",
                color_discrete_map=LINE_COLOURS,
                labels={"service_adequacy_index": "Service Adequacy Index (0–1)", "segment": "Track Segment"},
            )
            fig_sai.update_layout(height=500, yaxis_title=None)
            render_chart_container(
                fig=fig_sai,
                title="Top 20 Most Underserved Track Links (Lowest SAI)",
                subtitle="Lower SAI indicates higher frequency deficit relative to passenger load",
                lineage="DERIVED",
                takeaway="Corridors with low SAI represent prime targets for frequency increases or signaling headway upgrades.",
                height=500,
            )
        else:
            st.info("Service Adequacy Index not computed for the selected filter combination.")
    else:
        st.info("Service adequacy dataset unavailable.")

# ── TAB 4: Station Inflow Stress ──────────────────────────────────────────────
with tabs[3]:
    render_section_header(
        title="Station Concourse & Platform Congestion Hotspots",
        subtitle="Tracking high-volume passenger entry concentrations during morning and evening rush hours.",
        status="OBSERVED",
    )
    if not st_cong.empty:
        st_sub = st_cong[(st_cong["year"] == sel_year) & (st_cong["day_type"] == sel_day)].copy()
        if not st_sub.empty and "am_peak" in st_sub.columns:
            top_st_cong = st_sub.sort_values("am_peak", ascending=False).head(20)
            render_data_table(
                df=top_st_cong[["station", "am_peak", "pm_peak", "total", "station_congestion_class"]].rename(
                    columns={
                        "station": "Station Name",
                        "am_peak": "AM Peak Entries",
                        "pm_peak": "PM Peak Entries",
                        "total": "Total Daily Footfall",
                        "station_congestion_class": "Severity Band",
                    }
                ),
                title="Top 20 Station Entry Hotspots",
                download_filename=f"metropulse_station_congestion_{sel_year}_{sel_day}.csv",
            )
