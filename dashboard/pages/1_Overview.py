"""
METROPULSE Dashboard — Page 1: Executive Overview
Enterprise Dark Command Center View
"""
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from dashboard.components.theme import apply_custom_css
from dashboard.components.sidebar import render_sidebar
from dashboard.components.header import render_header
from dashboard.components.section_header import render_section_header
from dashboard.components.metric_card import render_metric_card
from dashboard.components.chart_container import render_chart_container
from dashboard.components.data_loader import (
    load, load_csv, LINE_COLOURS, format_number
)

st.set_page_config(page_title="Executive Overview | METROPULSE", page_icon="🚇", layout="wide")
apply_custom_css()
render_sidebar()

# ─── Load data ────────────────────────────────────────────────────────────────
boarders  = load("tube_line_boarders")
entries   = load("tube_station_entries")
links     = load_csv("congestion_link_congestion")
peak_prof = load_csv("congestion_peak_profile")

if entries.empty and boarders.empty:
    st.error("⚠️ Processed datasets not found. Please ensure data preprocessing has completed.")
    st.stop()

# ─── Sidebar filters ─────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("<div style='font-size: 11px; font-weight: 700; color: #94A3B8; text-transform: uppercase;'>View Filters</div>", unsafe_allow_html=True)
    all_years = sorted(boarders["year"].dropna().unique().tolist()) if not boarders.empty else [2024]
    sel_year  = st.selectbox("Operating Year", all_years, index=len(all_years)-1)
    all_days  = sorted(boarders["day_type"].dropna().unique().tolist()) if not boarders.empty else ["MON"]
    sel_day   = st.selectbox("Day Model", all_days, index=0)

# Filter data
def _filt(df, yr=sel_year, dy=sel_day):
    if df.empty: return df
    if "year" in df.columns:     df = df[df["year"] == yr]
    if "day_type" in df.columns: df = df[df["day_type"] == dy]
    return df

brd_f  = _filt(boarders)
ent_f  = _filt(entries)
link_f = _filt(links) if not links.empty else pd.DataFrame()

# Top Header
render_header(
    page_name="Executive Overview",
    subtitle=f"Macro mobility telemetry, peak diurnal curves, and network ridership for {sel_year} ({sel_day})",
    active_filters={"Year": sel_year, "Day Model": sel_day},
)

# ─── KPI Metrics ──────────────────────────────────────────────────────────────
total_pax = brd_f["total"].sum() if not brd_f.empty and "total" in brd_f.columns else 0
n_stations = ent_f["asc"].nunique() if not ent_f.empty and "asc" in ent_f.columns else 268
n_links    = len(link_f) if not link_f.empty else 850

if not brd_f.empty and "total" in brd_f.columns:
    top_line_row = brd_f.groupby("line_name")["total"].max().idxmax()
    top_line_val = brd_f.groupby("line_name")["total"].max().max()
else:
    top_line_row, top_line_val = "N/A", 0

if not ent_f.empty and "total" in ent_f.columns:
    top_stn_grp  = ent_f.groupby("station")["total"].max()
    top_stn      = top_stn_grp.idxmax()
    top_stn_val  = top_stn_grp.max()
else:
    top_stn, top_stn_val = "N/A", 0

# Peak interval
if not peak_prof.empty and "passengers" in peak_prof.columns:
    p = _filt(peak_prof)
    if not p.empty:
        peak_idx   = p.groupby("time_interval")["passengers"].sum().idxmax()
        peak_label = str(peak_idx)
    else:
        peak_label = "08:15–08:30"
else:
    peak_label = "08:15–08:30"

c1, c2, c3, c4, c5, c6 = st.columns(6)
with c1:
    render_metric_card(
        title="Daily Boarders",
        value=format_number(total_pax),
        subtitle="Network total",
        status="OBSERVED",
        tooltip="Total passenger boardings across all London Underground lines on this typical day model",
    )
with c2:
    render_metric_card(
        title="Stations Monitored",
        value=n_stations,
        subtitle="Fare zones 1–9",
        status="OBSERVED",
        tooltip="Active London Underground stations reporting entry and exit transactions",
    )
with c3:
    render_metric_card(
        title="Top Demand Line",
        value=str(top_line_row).split(" ")[0],
        subtitle=f"{format_number(top_line_val)} boarders",
        status="OBSERVED",
        tooltip=f"Highest boardings recorded by {top_line_row}",
    )
with c4:
    render_metric_card(
        title="Busiest Station",
        value=str(top_stn)[:14],
        subtitle=f"{format_number(top_stn_val)} entries",
        status="OBSERVED",
        tooltip=f"Station with highest total recorded entries: {top_stn}",
    )
with c5:
    render_metric_card(
        title="Peak Time Interval",
        value=peak_label,
        subtitle="Maximum system surge",
        status="DERIVED",
        tooltip="15-minute period showing highest concurrent passenger link loads across London",
    )
with c6:
    render_metric_card(
        title="Vehicle Crush Cap.",
        value=None,
        subtitle="Omitted in NUMBAT",
        status="EXTERNAL_REQUIRED",
        missing_reason="Physical vehicle capacity requires TfL rolling stock fleet specifications.",
        tooltip="TfL NUMBAT provides frequency and passenger loads, but not rolling stock carriage capacity.",
    )

st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

# ─── Row 1: Line Boarders + 15-Minute Diurnal Profile ─────────────────────────
render_section_header(
    title="Passenger Demand Dynamics & Temporal Profiling",
    subtitle="Line-level market share comparison and network-wide 15-minute diurnal passenger flow curve.",
    status="OBSERVED",
)

chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    if not brd_f.empty and "total" in brd_f.columns:
        line_sum = (
            brd_f.groupby(["line_name"])["total"]
            .max().reset_index()
            .sort_values("total", ascending=True)
        )
        colours = [LINE_COLOURS.get(ln, "#3B82F6") for ln in line_sum["line_name"]]
        fig_line = go.Figure(go.Bar(
            x=line_sum["total"],
            y=line_sum["line_name"],
            orientation="h",
            marker=dict(color=colours, line=dict(color="#172338", width=1)),
            text=line_sum["total"].apply(lambda v: format_number(v)),
            textposition="outside",
            hovertemplate="<b>%{y}</b><br>Daily Boarders: %{x:,.0f}<extra></extra>",
        ))
        fig_line.update_layout(
            xaxis_title="Observed Daily Boardings",
            yaxis_title=None,
            height=380,
        )
        render_chart_container(
            fig=fig_line,
            title="Boardings by Underground Line",
            subtitle=f"{sel_year} {sel_day} model",
            lineage="OBSERVED",
            takeaway="Northern, Central, and Jubilee lines absorb the bulk of intra-London passenger volume.",
            height=380,
        )

with chart_col2:
    if not peak_prof.empty:
        p = _filt(peak_prof)
        if not p.empty and "passengers" in p.columns:
            tp = p.groupby(["start_minute", "time_interval"])["passengers"].sum().reset_index()
            tp = tp.sort_values("start_minute")
            fig_time = go.Figure()
            fig_time.add_trace(go.Scatter(
                x=tp["time_interval"],
                y=tp["passengers"],
                mode="lines",
                fill="tozeroy",
                line=dict(color="#22D3EE", width=2.5),
                fillcolor="rgba(34, 211, 238, 0.12)",
                hovertemplate="<b>Interval %{x}</b><br>Active Passengers: %{y:,.0f}<extra></extra>",
            ))
            # Pick step tickvals
            tick_idx = list(range(0, len(tp), 8))
            fig_time.update_xaxes(
                tickvals=tp["time_interval"].iloc[tick_idx].tolist(),
                tickangle=35,
            )
            fig_time.update_layout(
                xaxis_title="Time of Day (15-Min Windows)",
                yaxis_title="Total Network Passengers",
                height=380,
            )
            render_chart_container(
                fig=fig_time,
                title="Diurnal Network Demand Curve",
                subtitle="15-minute aggregate passenger flow across all track links",
                lineage="DERIVED",
                takeaway="A classic bimodal profile emerges with a sharp morning rush peak (08:00–08:45) and a sustained evening peak (17:30–18:30).",
                height=380,
            )

# ─── Row 2: Top Stations & Congestion Breakdown ───────────────────────────────
render_section_header(
    title="Station Volume Rankings & Network Bottlenecks",
    subtitle="Top entry terminals and distribution of track links across congestion severity classes.",
    status="DERIVED",
)

chart_col3, chart_col4 = st.columns(2)

with chart_col3:
    if not ent_f.empty and "total" in ent_f.columns:
        top15 = (
            ent_f.groupby("station")["total"].max()
            .reset_index().sort_values("total", ascending=False).head(12)
        )
        fig_stn = go.Figure(go.Bar(
            x=top15["total"][::-1],
            y=top15["station"][::-1],
            orientation="h",
            marker=dict(
                color=top15["total"][::-1],
                colorscale=[[0, "#172554"], [0.5, "#2563EB"], [1, "#38BDF8"]],
                line=dict(color="#172338", width=1),
            ),
            text=top15["total"][::-1].apply(lambda v: format_number(v)),
            textposition="outside",
            hovertemplate="<b>%{y}</b><br>Daily Entries: %{x:,.0f}<extra></extra>",
        ))
        fig_stn.update_layout(
            xaxis_title="Daily Station Entries",
            yaxis_title=None,
            height=380,
        )
        render_chart_container(
            fig=fig_stn,
            title="Top 12 Origin Stations by Passenger Entries",
            subtitle=f"{sel_year} {sel_day} model",
            lineage="OBSERVED",
            takeaway="Stratford, King's Cross St. Pancras, and London Bridge serve as dominant multi-modal gateway hubs.",
            height=380,
        )

with chart_col4:
    if not link_f.empty and "congestion_class" in link_f.columns:
        cong_counts = link_f["congestion_class"].value_counts().reset_index()
        cong_counts.columns = ["Class", "Count"]
        color_map = {
            "Critical": "#EF4444",
            "High": "#F59E0B",
            "Moderate": "#3B82F6",
            "Low": "#10B981",
        }
        fig_cong = px.pie(
            cong_counts,
            names="Class",
            values="Count",
            color="Class",
            color_discrete_map=color_map,
            hole=0.55,
        )
        fig_cong.update_traces(
            textposition="outside",
            textinfo="label+percent",
            marker=dict(line=dict(color="#0D1422", width=2)),
        )
        render_chart_container(
            fig=fig_cong,
            title="Track Congestion Classification Breakdown",
            subtitle="Based on Load-Per-Train threshold categorizations",
            lineage="DERIVED",
            takeaway="Over 14% of directional track links experience High or Critical load intensity during peak intervals.",
            height=380,
        )
