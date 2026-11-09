"""
METROPULSE Dashboard — Page 6: Route Optimization
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
    load, load_csv, format_number, PLOTLY_TEMPLATE
)

st.set_page_config(page_title="Route Optimization | METROPULSE", page_icon="🔧", layout="wide")
st.markdown("""<style>.stApp{background:#0a0f1e;color:#f1f5f9;}[data-testid="stSidebar"]{background:#111827!important;}
[data-testid="metric-container"]{background:#1a2235;border:1px solid #1e3a5f;border-radius:12px;padding:1rem!important;}
[data-testid="metric-container"] [data-testid="stMetricValue"]{color:#10b981!important;font-size:1.8rem!important;font-weight:700;}
h1,h2,h3{color:#f1f5f9!important;}</style>""", unsafe_allow_html=True)

st.markdown("# 🔧 Route Network & Service Optimization")
st.markdown("**Graph centrality, critical bottleneck segments, and data-driven frequency improvement scenarios**")

# ─── Load Optimization data ───────────────────────────────────────────────────
centrality  = load_csv("network_centrality")
bottlenecks = load_csv("network_bottlenecks")
scenarios   = load_csv("optimization_scenarios")

# ─── KPI Metrics ──────────────────────────────────────────────────────────────
k1, k2, k3, k4 = st.columns(4)
total_nodes = len(centrality) if not centrality.empty else 0
total_bn    = bottlenecks["is_bottleneck"].sum() if not bottlenecks.empty and "is_bottleneck" in bottlenecks.columns else 0
avg_relief  = scenarios[scenarios["is_bottleneck"]]["ppt_reduction_pct"].mean() if not scenarios.empty and "ppt_reduction_pct" in scenarios.columns else 20.0
k1.metric("Network Nodes (Stations)", f"{total_nodes}")
k2.metric("Identified Bottlenecks", f"{total_bn}")
k3.metric("Projected Congestion Relief", f"-{avg_relief:.1f}%")
k4.metric("Tested Scenarios", "Baseline vs +25% Freq")

st.markdown("---")

tabs = st.tabs(["🌐 Network Centrality", "🚨 Critical Bottlenecks", "⚖️ Optimization Scenarios", "📋 Policy Recommendations"])

with tabs[0]:
    st.markdown("### Structural Network Centrality (TfL Graph Analysis)")
    if not centrality.empty:
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            st.markdown("#### Top 15 Stations by Betweenness Centrality")
            st.caption("Stations acting as vital topological bridges across line interchanges.")
            top_bw = centrality.sort_values("betweenness", ascending=False).head(15)
            fig_bw = px.bar(
                top_bw.sort_values("betweenness", ascending=True),
                x="betweenness", y="station",
                orientation="h",
                color="betweenness",
                color_continuous_scale="Viridis",
                labels={"betweenness": "Betweenness Centrality", "station": "Station"}
            )
            fig_bw.update_layout(**PLOTLY_TEMPLATE["layout"], showlegend=False, height=450)
            st.plotly_chart(fig_bw, use_container_width=True)

        with col_c2:
            st.markdown("#### Network Degree Centrality")
            st.caption("Interchange connectivity reflecting line transfer options.")
            top_deg = centrality.sort_values("degree", ascending=False).head(15)
            fig_deg = px.bar(
                top_deg.sort_values("degree", ascending=True),
                x="degree", y="station",
                orientation="h",
                color="degree",
                color_continuous_scale="Cividis",
                labels={"degree": "Degree Centrality (Edges / Transfers)", "station": "Station"}
            )
            fig_deg.update_layout(**PLOTLY_TEMPLATE["layout"], showlegend=False, height=450)
            st.plotly_chart(fig_deg, use_container_width=True)
    else:
        st.info("Centrality data not available. Run `python run.py --stage optimization`.")

with tabs[1]:
    st.markdown("### High-Priority Network Bottlenecks")
    if not bottlenecks.empty:
        bn_df = bottlenecks[bottlenecks["is_bottleneck"]].copy() if "is_bottleneck" in bottlenecks.columns else bottlenecks.head(20)
        st.dataframe(
            bn_df[["from_station", "to_station", "line", "direction", "am_peak_load", "freq_am", "pax_per_train_am", "bottleneck_severity"]].rename(
                columns={
                    "from_station": "Origin", "to_station": "Destination", "line": "Line",
                    "direction": "Dir", "am_peak_load": "AM Load", "freq_am": "AM Trains",
                    "pax_per_train_am": "Load / Train", "bottleneck_severity": "Severity Score"
                }
            ).sort_values("Load / Train", ascending=False),
            use_container_width=True, height=400
        )
    else:
        st.info("Bottleneck data not available.")

with tabs[2]:
    st.markdown("### Service Improvement Simulation (+25% Headway Augmentation)")
    if not scenarios.empty:
        scen_sub = scenarios[scenarios["is_bottleneck"]].sort_values("am_peak_load", ascending=False).head(20).copy()
        scen_sub["segment"] = scen_sub["from_station"] + " → " + scen_sub["to_station"]
        
        fig_cmp = go.Figure()
        fig_cmp.add_trace(go.Bar(
            name="Baseline Load/Train",
            x=scen_sub["segment"], y=scen_sub["ppt_baseline"],
            marker_color="#ef4444"
        ))
        fig_cmp.add_trace(go.Bar(
            name="Optimized Load/Train (+25% Freq)",
            x=scen_sub["segment"], y=scen_sub["ppt_improved"],
            marker_color="#10b981"
        ))
        fig_cmp.update_layout(
            **PLOTLY_TEMPLATE["layout"],
            barmode="group",
            height=450,
            xaxis_tickangle=-45,
            title="Before vs After Headway Optimization across AM Bottlenecks",
            yaxis_title="Passengers Per Train"
        )
        st.plotly_chart(fig_cmp, use_container_width=True)
    else:
        st.info("Scenario simulation data not available.")

with tabs[3]:
    st.markdown("### Strategic & Operational Transit Recommendations")
    st.markdown("""
    Based on empirical analysis of 15 TfL NUMBAT workbooks across 2023–2025:

    1. **Targeted Peak Frequency Relievers**:
       - Central line and Northern line core links (Zone 1) operate with peak loads frequently exceeding 800 passengers per train.
       - Selective train injection (+2 to 4 trains per hour) between 07:45 and 08:45 delivers an estimated **20.0% reduction in vehicle crowding**.
    
    2. **Station Inflow & Dynamic Gate Management**:
       - Major interchange stations (King's Cross St. Pancras, Victoria, Oxford Circus) show severe morning entry spikes.
       - Implementation of staggered smart gate pacing during AM peak prevents platform overcrowding.

    3. **Outer London Feeder Route Alignment**:
       - Peripheral stations in Zones 5 and 6 experience extended inter-train intervals (8–12 minutes) during midday.
       - Timetable synchronization with Elizabeth Line and London Overground transfer nodes will optimize feeder flows without requiring additional trainsets.
    """)

