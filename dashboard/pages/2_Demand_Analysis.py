"""
METROPULSE Dashboard — Page 2: Passenger Demand Analysis
"""
import sys
from pathlib import Path
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

ROOT = Path(__file__).parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from dashboard.components.data_loader import (
    load, load_csv, LINE_COLOURS, format_number, PLOTLY_TEMPLATE
)

st.set_page_config(page_title="Demand | METROPULSE", page_icon="📊", layout="wide")
st.markdown("""<style>.stApp{background:#0a0f1e;color:#f1f5f9;}[data-testid="stSidebar"]{background:#111827!important;}
[data-testid="metric-container"]{background:#1a2235;border:1px solid #1e3a5f;border-radius:12px;padding:1rem!important;}
[data-testid="metric-container"] [data-testid="stMetricValue"]{color:#3b82f6!important;font-size:1.8rem!important;font-weight:700;}
h1,h2,h3{color:#f1f5f9!important;}</style>""", unsafe_allow_html=True)

st.markdown("# 📈 Passenger Demand Analysis")

# ─── Load data ────────────────────────────────────────────────────────────────
boarders  = load("tube_line_boarders")
entries   = load("tube_station_entries")
exits     = load("tube_station_exits")
st_brd    = load("tube_station_boarders")
st_ali    = load("tube_station_alighters")

# ─── Sidebar filters ─────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("**Filters**")
    all_years = sorted(entries["year"].dropna().unique()) if not entries.empty else [2024]
    sel_years = st.multiselect("Year", all_years, default=all_years)
    all_days  = sorted(entries["day_type"].dropna().unique()) if not entries.empty else ["MON"]
    sel_days  = st.multiselect("Day Type", all_days, default=["MON","TWT","FRI"])

def _filt(df, yr_col="year", day_col="day_type"):
    if df.empty: return df
    if yr_col  in df.columns: df = df[df[yr_col].isin(sel_years)]
    if day_col in df.columns: df = df[df[day_col].isin(sel_days)]
    return df

ent_f  = _filt(entries)
ext_f  = _filt(exits)
brd_f  = _filt(boarders)
sbrd_f = _filt(st_brd)
sali_f = _filt(st_ali)

# ─── Tab layout ───────────────────────────────────────────────────────────────
tabs = st.tabs([
    "🏛️ Stations", "🚇 Lines", "⏱️ Time of Day",
    "📅 Weekday/Weekend", "📆 Year Comparison"
])

# ── TAB 1: Station demand ─────────────────────────────────────────────────────
with tabs[0]:
    col_a, col_b = st.columns([2, 1])

    with col_a:
        st.markdown("### Station Entry Rankings")
        if not ent_f.empty and "total" in ent_f.columns:
            st_rank = (
                ent_f.groupby("station")["total"].mean()
                .reset_index().sort_values("total", ascending=False)
            )
            n_show = st.slider("Show top N stations", 10, 50, 25)
            top_df = st_rank.head(n_show).sort_values("total")
            fig = go.Figure(go.Bar(
                x=top_df["total"], y=top_df["station"],
                orientation="h",
                marker=dict(color=top_df["total"],
                            colorscale=[[0,"#1e3a5f"],[0.5,"#3b82f6"],[1,"#06b6d4"]]),
                hovertemplate="<b>%{y}</b><br>Mean daily entries: %{x:,.0f}<extra></extra>",
            ))
            fig.update_layout(**PLOTLY_TEMPLATE["layout"], height=600,
                              xaxis_title="Mean Daily Entries",
                              margin=dict(l=0,r=60,t=10,b=40))
            st.plotly_chart(fig, use_container_width=True)

    with col_b:
        st.markdown("### Entry vs Exit")
        if not ent_f.empty and not ext_f.empty and "total" in ent_f.columns:
            ent_sum = ent_f.groupby("station")["total"].mean().reset_index().rename(columns={"total":"entries"})
            ext_sum = ext_f.groupby("station")["total"].mean().reset_index().rename(columns={"total":"exits"})
            merged  = ent_sum.merge(ext_sum, on="station").dropna()
            top_cmp = merged.sort_values("entries", ascending=False).head(20)
            fig2 = go.Figure()
            fig2.add_trace(go.Bar(name="Entries", x=top_cmp["station"],
                                   y=top_cmp["entries"], marker_color="#3b82f6"))
            fig2.add_trace(go.Bar(name="Exits",   x=top_cmp["station"],
                                   y=top_cmp["exits"],   marker_color="#06b6d4"))
            fig2.update_layout(**PLOTLY_TEMPLATE["layout"], barmode="group",
                               height=350, xaxis_tickangle=-45,
                               margin=dict(l=0,r=0,t=10,b=100))
            st.plotly_chart(fig2, use_container_width=True)

        # Inflow/outflow asymmetry
        st.markdown("### Inflow/Outflow Asymmetry")
        asym = load_csv("temporal_station_flow_asymmetry")
        asym_f = _filt(asym)
        if not asym_f.empty and "net_flow" in asym_f.columns:
            top_net = (
                asym_f.groupby("station")["net_flow"].mean()
                .reset_index().sort_values("net_flow", key=abs, ascending=False).head(15)
            )
            top_net["colour"] = top_net["net_flow"].apply(
                lambda v: "#10b981" if v > 0 else "#ef4444")
            fig3 = go.Figure(go.Bar(
                x=top_net["net_flow"], y=top_net["station"],
                orientation="h", marker_color=top_net["colour"],
                hovertemplate="<b>%{y}</b><br>Net flow (entries−exits): %{x:,.0f}<extra></extra>",
            ))
            fig3.update_layout(**PLOTLY_TEMPLATE["layout"], height=350,
                               xaxis_title="Net Flow",
                               margin=dict(l=0,r=0,t=10,b=40))
            st.plotly_chart(fig3, use_container_width=True)

# ── TAB 2: Line demand ────────────────────────────────────────────────────────
with tabs[1]:
    if not brd_f.empty and "total" in brd_f.columns:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### Total Boarders by Line")
            ln_sum = (
                brd_f.groupby("line_name")["total"].mean()
                .reset_index().sort_values("total", ascending=True)
            )
            colours = [LINE_COLOURS.get(ln, "#3b82f6") for ln in ln_sum["line_name"]]
            fig = go.Figure(go.Bar(
                x=ln_sum["total"], y=ln_sum["line_name"],
                orientation="h", marker_color=colours,
                text=ln_sum["total"].apply(format_number), textposition="outside",
                hovertemplate="<b>%{y}</b><br>Mean daily boarders: %{x:,.0f}<extra></extra>",
            ))
            fig.update_layout(**PLOTLY_TEMPLATE["layout"], height=400,
                              xaxis_title="Mean Daily Boarders",
                              margin=dict(l=0,r=80,t=10,b=40))
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.markdown("### Period Breakdown by Line")
            period_cols = [c for c in ["early","am_peak","midday","pm_peak","evening","late"]
                           if c in brd_f.columns]
            if period_cols:
                ln_period = brd_f.groupby("line_name")[period_cols].mean().reset_index()
                fig2 = px.bar(
                    ln_period.melt(id_vars="line_name", value_vars=period_cols,
                                   var_name="period", value_name="boarders"),
                    x="line_name", y="boarders", color="period", barmode="stack",
                    color_discrete_sequence=["#1d4ed8","#3b82f6","#60a5fa","#93c5fd","#06b6d4","#0891b2"],
                    labels={"boarders":"Boarders","line_name":"Line"},
                )
                fig2.update_layout(**PLOTLY_TEMPLATE["layout"], height=400,
                                   xaxis_tickangle=-30, margin=dict(l=0,r=0,t=10,b=80))
                st.plotly_chart(fig2, use_container_width=True)

# ── TAB 3: Time of Day ────────────────────────────────────────────────────────
with tabs[2]:
    st.markdown("### Demand Profile by 15-Minute Interval")
    if not ent_f.empty and "passengers" in ent_f.columns and "start_minute" in ent_f.columns:
        tp = (
            ent_f[ent_f["start_minute"] >= 0]
            .groupby(["start_minute","time_interval"])["passengers"]
            .sum().reset_index().sort_values("start_minute")
        )
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=tp["time_interval"], y=tp["passengers"],
            mode="lines", fill="tozeroy",
            line=dict(color="#3b82f6", width=2),
            fillcolor="rgba(59,130,246,0.15)",
            name="Total Passengers",
        ))
        # Shade AM/PM peaks
        for x0, x1, label, col in [("0630-0645","0930-0945","AM Peak","rgba(239,68,68,0.1)"),
                                     ("1600-1615","1900-1915","PM Peak","rgba(245,158,11,0.1)")]:
            fig.add_vrect(x0=x0, x1=x1, fillcolor=col, line_width=0,
                          annotation_text=label, annotation_position="top left")
        fig.update_layout(**PLOTLY_TEMPLATE["layout"], height=400,
                          xaxis_title="15-Minute Interval", yaxis_title="Passengers",
                          margin=dict(l=0,r=0,t=10,b=60))
        tick_step = max(1, len(tp)//16)
        fig.update_xaxes(tickvals=tp["time_interval"].iloc[::tick_step].tolist(), tickangle=45)
        st.plotly_chart(fig, use_container_width=True)

        # Heat map: periods by line
        if not sbrd_f.empty and "passengers" in sbrd_f.columns:
            st.markdown("### Period Demand Heatmap by Line")
            period_piv = (
                sbrd_f[sbrd_f["start_minute"] >= 0]
                .groupby(["line","period"])["passengers"].sum()
                .reset_index()
            )
            if not period_piv.empty:
                heat = period_piv.pivot_table(index="line", columns="period",
                                               values="passengers", fill_value=0)
                col_order = [c for c in ["Early","AM Peak","Midday","PM Peak","Evening","Late"]
                             if c in heat.columns]
                heat = heat[col_order] if col_order else heat
                fig2 = px.imshow(heat,
                                  color_continuous_scale=[[0,"#0a0f1e"],[0.5,"#3b82f6"],[1,"#06b6d4"]],
                                  labels=dict(x="Period", y="Line", color="Passengers"))
                fig2.update_layout(**PLOTLY_TEMPLATE["layout"], height=350,
                                   margin=dict(l=0,r=0,t=10,b=40))
                st.plotly_chart(fig2, use_container_width=True)

# ── TAB 4: Weekday/Weekend ────────────────────────────────────────────────────
with tabs[3]:
    st.markdown("### Weekday vs Weekend Demand Comparison")
    wk = load_csv("temporal_weekday_weekend")
    if not wk.empty:
        wk_f = wk[wk["year"].isin(sel_years)] if "year" in wk.columns else wk
        wk_f["day_category"] = wk_f["is_weekend"].map({True:"Weekend",False:"Weekday",1:"Weekend",0:"Weekday"})
        fig = px.line(
            wk_f.groupby(["start_minute","day_category","year"])["passengers"].sum().reset_index(),
            x="start_minute", y="passengers", color="day_category",
            line_dash="year" if wk_f["year"].nunique() > 1 else None,
            color_discrete_map={"Weekday":"#3b82f6","Weekend":"#10b981"},
            labels={"start_minute":"Minutes since midnight","passengers":"Passengers"},
        )
        fig.update_layout(**PLOTLY_TEMPLATE["layout"], height=400,
                          xaxis_title="Minutes Since Midnight",
                          margin=dict(l=0,r=0,t=10,b=40))
        st.plotly_chart(fig, use_container_width=True)

        # Day type total comparison
        st.markdown("### Total Demand by Day Type")
        day_cmp = load_csv("temporal_day_type_comparison")
        if not day_cmp.empty:
            day_f = day_cmp[day_cmp["year"].isin(sel_years)] if "year" in day_cmp.columns else day_cmp
            fig2 = px.bar(
                day_f, x="day_type_label", y="total", color="year",
                barmode="group",
                color_discrete_sequence=["#1e40af","#3b82f6","#93c5fd"],
                labels={"total":"Total Boarders","day_type_label":"Day Type"},
            )
            fig2.update_layout(**PLOTLY_TEMPLATE["layout"], height=350,
                               margin=dict(l=0,r=0,t=10,b=40))
            st.plotly_chart(fig2, use_container_width=True)

# ── TAB 5: Year Comparison ────────────────────────────────────────────────────
with tabs[4]:
    st.markdown("### 2023 vs 2024 vs 2025 Demand Profiles")
    yoy = load_csv("temporal_yoy_line_boarders")
    if not yoy.empty:
        yr_cols = [c for c in yoy.columns if str(c).isdigit()]
        if yr_cols:
            day_sel_yoy = st.selectbox("Day type for YoY", sorted(yoy["day_type"].unique()))
            yoy_sel = yoy[yoy["day_type"] == day_sel_yoy]
            yoy_m = yoy_sel.melt(id_vars=["line_name","day_type"],
                                  value_vars=yr_cols,
                                  var_name="year", value_name="boarders")
            fig = px.bar(
                yoy_m, x="line_name", y="boarders", color="year",
                barmode="group",
                color_discrete_sequence=["#1e40af","#3b82f6","#93c5fd"],
                labels={"boarders":"Daily Boarders","line_name":"Line"},
            )
            fig.update_layout(**PLOTLY_TEMPLATE["layout"], height=450,
                              xaxis_tickangle=-30, margin=dict(l=0,r=0,t=10,b=80))
            st.plotly_chart(fig, use_container_width=True)

            # Growth table
            if len(yr_cols) >= 2:
                yr_sorted = sorted(yr_cols)
                yoy_sel = yoy_sel.copy()
                for i in range(1, len(yr_sorted)):
                    yy_prev, yy_curr = yr_sorted[i-1], yr_sorted[i]
                    if yy_prev in yoy_sel.columns and yy_curr in yoy_sel.columns:
                        yoy_sel[f"Growth {yy_prev}→{yy_curr}"] = (
                            (yoy_sel[yy_curr] - yoy_sel[yy_prev]) /
                            yoy_sel[yy_prev].replace(0, float("nan")) * 100
                        ).round(1)
                disp_cols = ["line_name"] + yr_sorted + [c for c in yoy_sel.columns if "Growth" in str(c)]
                disp_cols = [c for c in disp_cols if c in yoy_sel.columns]
                st.dataframe(yoy_sel[disp_cols].rename(columns={"line_name":"Line"}),
                             use_container_width=True, height=300)

