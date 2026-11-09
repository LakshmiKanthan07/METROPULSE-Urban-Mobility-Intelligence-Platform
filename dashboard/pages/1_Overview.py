"""
METROPULSE Dashboard — Page 1: Executive Overview
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
    load, load_csv, load_bi, load_coords,
    LINE_COLOURS, LINE_CODE_TO_NAME, format_number, PLOTLY_TEMPLATE
)

st.set_page_config(page_title="Overview | METROPULSE", page_icon="🚇", layout="wide")

# Apply shared CSS (duplicated header for multi-page)
st.markdown("""
<style>
.stApp{background:#0a0f1e;color:#f1f5f9;}
[data-testid="stSidebar"]{background:#111827!important;}
[data-testid="metric-container"]{background:#1a2235;border:1px solid #1e3a5f;border-radius:12px;padding:1rem!important;}
[data-testid="metric-container"] [data-testid="stMetricLabel"]{color:#94a3b8!important;font-size:.75rem!important;text-transform:uppercase;}
[data-testid="metric-container"] [data-testid="stMetricValue"]{color:#3b82f6!important;font-size:1.8rem!important;font-weight:700;}
h1,h2,h3{color:#f1f5f9!important;}
</style>
""", unsafe_allow_html=True)

st.markdown("# 📊 Executive Overview")
st.markdown("**Key performance indicators and demand summary across the London Underground network**")

# ─── Load data ────────────────────────────────────────────────────────────────
boarders  = load("tube_line_boarders")
entries   = load("tube_station_entries")
links     = load_csv("congestion_link_congestion")
peak_prof = load_csv("congestion_peak_profile")

if entries.empty and boarders.empty:
    st.error("⚠️ Processed data not found. Please run `python run.py --stage preprocess` first.")
    st.stop()

# ─── Sidebar filters ─────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("**Filters**")
    all_years = sorted(boarders["year"].dropna().unique()) if not boarders.empty else [2024]
    sel_year  = st.selectbox("Year", all_years, index=len(all_years)-1)
    all_days  = sorted(boarders["day_type"].dropna().unique()) if not boarders.empty else ["MON"]
    sel_day   = st.selectbox("Day Type", all_days, index=0)

# ─── Filter data ──────────────────────────────────────────────────────────────
def _filt(df, yr=sel_year, dy=sel_day):
    if df.empty: return df
    if "year" in df.columns:     df = df[df["year"] == yr]
    if "day_type" in df.columns: df = df[df["day_type"] == dy]
    return df

brd_f  = _filt(boarders)
ent_f  = _filt(entries)
link_f = _filt(links) if not links.empty else pd.DataFrame()

# ─── KPI Metrics ──────────────────────────────────────────────────────────────
col1, col2, col3, col4, col5, col6 = st.columns(6)

total_pax = brd_f["total"].sum() if not brd_f.empty and "total" in brd_f.columns else 0
n_stations = ent_f["asc"].nunique() if not ent_f.empty and "asc" in ent_f.columns else 0
n_lines    = brd_f["line_code"].nunique() if not brd_f.empty else 0

# Top line
if not brd_f.empty and "total" in brd_f.columns:
    top_line_row = brd_f.groupby("line_name")["total"].max().idxmax()
    top_line_val = brd_f.groupby("line_name")["total"].max().max()
else:
    top_line_row, top_line_val = "N/A", 0

# Top station
if not ent_f.empty and "total" in ent_f.columns:
    top_stn_grp  = ent_f.groupby("station")["total"].max()
    top_stn      = top_stn_grp.idxmax()
    top_stn_val  = top_stn_grp.max()
else:
    top_stn, top_stn_val = "N/A", 0

# Peak hour
if not peak_prof.empty and "passengers" in peak_prof.columns:
    p = _filt(peak_prof)
    if not p.empty:
        peak_idx   = p.groupby("time_interval")["passengers"].sum().idxmax()
        peak_label = str(peak_idx)
    else:
        peak_label = "N/A"
else:
    peak_label = "07:30–08:30"

col1.metric("🚶 Total Boarders", format_number(total_pax))
col2.metric("🏛️ LU Stations",    f"{n_stations}")
col3.metric("🚇 LU Lines",       f"{n_lines}")
col4.metric("🏆 Top Line",       top_line_row.split(" ")[0] if top_line_row != "N/A" else "N/A")
col5.metric("⭐ Top Station",    str(top_stn)[:15])
col6.metric("⏰ Peak Interval",  peak_label)

st.markdown("---")

# ─── Charts Row 1: Line boarders + Time profile ───────────────────────────────
c1, c2 = st.columns([1, 1])

with c1:
    st.markdown("### Boarders by Line")
    if not brd_f.empty and "total" in brd_f.columns:
        line_sum = (
            brd_f.groupby(["line_name"])["total"]
            .max().reset_index()
            .sort_values("total", ascending=True)
        )
        colours = [LINE_COLOURS.get(ln, "#3b82f6") for ln in line_sum["line_name"]]
        fig = go.Figure(go.Bar(
            x=line_sum["total"], y=line_sum["line_name"],
            orientation="h",
            marker_color=colours,
            text=line_sum["total"].apply(lambda v: format_number(v)),
            textposition="outside",
            hovertemplate="<b>%{y}</b><br>Boarders: %{x:,.0f}<extra></extra>",
        ))
        fig.update_layout(
            **PLOTLY_TEMPLATE["layout"],
            height=350, showlegend=False,
            xaxis_title="Daily Boarders",
            yaxis_title=None,
            margin=dict(l=0, r=60, t=20, b=40),
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No boarder data for selected filters.")

with c2:
    st.markdown("### Demand by Time of Day")
    if not peak_prof.empty:
        p = _filt(peak_prof)
        if not p.empty and "passengers" in p.columns:
            tp = p.groupby(["start_minute", "time_interval"])["passengers"].sum().reset_index()
            tp = tp.sort_values("start_minute")
            fig2 = go.Figure(go.Scatter(
                x=tp["time_interval"], y=tp["passengers"],
                mode="lines", fill="tozeroy",
                line=dict(color="#3b82f6", width=2),
                fillcolor="rgba(59,130,246,0.15)",
                hovertemplate="<b>%{x}</b><br>Passengers: %{y:,.0f}<extra></extra>",
            ))
            fig2.update_layout(
                **PLOTLY_TEMPLATE["layout"],
                height=350,
                xaxis_title="15-Minute Interval",
                yaxis_title="Passengers",
                margin=dict(l=0, r=0, t=20, b=40),
            )
            # Only show every 4th label
            tick_indices = list(range(0, len(tp), 4))
            fig2.update_xaxes(
                tickvals=tp["time_interval"].iloc[tick_indices].tolist(),
                tickangle=45,
            )
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("No time-profile data for selected filters.")
    else:
        st.info("Run analytics stage to see time profile.")

# ─── Charts Row 2: Top stations + YoY comparison ─────────────────────────────
c3, c4 = st.columns([1, 1])

with c3:
    st.markdown("### Top 15 Stations by Entries")
    if not ent_f.empty and "total" in ent_f.columns:
        top15 = (
            ent_f.groupby("station")["total"].max()
            .reset_index().sort_values("total", ascending=False).head(15)
        )
        fig3 = go.Figure(go.Bar(
            x=top15["total"][::-1],
            y=top15["station"][::-1],
            orientation="h",
            marker=dict(
                color=top15["total"][::-1],
                colorscale=[[0, "#1e3a5f"], [0.5, "#3b82f6"], [1, "#06b6d4"]],
            ),
            text=top15["total"][::-1].apply(lambda v: format_number(v)),
            textposition="outside",
            hovertemplate="<b>%{y}</b><br>Entries: %{x:,.0f}<extra></extra>",
        ))
        fig3.update_layout(
            **PLOTLY_TEMPLATE["layout"],
            height=400, showlegend=False,
            xaxis_title="Daily Entries",
            yaxis_title=None,
            margin=dict(l=0, r=70, t=20, b=40),
        )
        st.plotly_chart(fig3, use_container_width=True)

with c4:
    st.markdown("### Year-on-Year Line Comparison")
    yoy = load_csv("temporal_yoy_line_boarders")
    if not yoy.empty:
        # Melt wide format
        yr_cols = [c for c in yoy.columns if str(c).isdigit()]
        if yr_cols:
            yoy_m = yoy[yoy["day_type"] == sel_day].melt(
                id_vars=["line_name"],
                value_vars=yr_cols,
                var_name="year",
                value_name="boarders",
            )
            fig4 = px.bar(
                yoy_m, x="line_name", y="boarders", color="year",
                barmode="group",
                color_discrete_sequence=["#1e40af","#3b82f6","#93c5fd"],
                labels={"boarders": "Daily Boarders", "line_name": "Line"},
            )
            fig4.update_layout(
                **PLOTLY_TEMPLATE["layout"],
                height=400,
                xaxis_tickangle=-30,
                legend_title="Year",
                margin=dict(l=0, r=0, t=20, b=80),
            )
            st.plotly_chart(fig4, use_container_width=True)
        else:
            st.info("Year-on-year data not available.")
    else:
        st.info("Run analytics stage to see YoY comparison.")

# ─── Congestion summary ───────────────────────────────────────────────────────
st.markdown("### 🔥 Congestion Overview")
if not link_f.empty and "congestion_class" in link_f.columns:
    cong_counts = link_f["congestion_class"].value_counts().reset_index()
    cong_counts.columns = ["Class", "Links"]
    cmap = {"Critical":"#ef4444","High":"#f59e0b","Moderate":"#3b82f6","Low":"#10b981"}
    cc1, cc2, cc3, cc4 = st.columns(4)
    for col, cls in zip([cc1,cc2,cc3,cc4], ["Critical","High","Moderate","Low"]):
        cnt = cong_counts[cong_counts["Class"]==cls]["Links"].sum() if cls in cong_counts["Class"].values else 0
        col.metric(f"🔴 {cls}" if cls=="Critical" else f"🟡 {cls}" if cls=="High" else f"🔵 {cls}" if cls=="Moderate" else f"🟢 {cls}", f"{cnt} links")
else:
    st.info("Run analytics stage to see congestion summary.")

