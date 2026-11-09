"""
METROPULSE — Streamlit Dashboard Main Entry Point
Urban Mobility Intelligence Platform
DataNova Global Data-thon 2026
"""
import sys
from pathlib import Path

import streamlit as st

# ─── Path setup ───────────────────────────────────────────────────────────────
ROOT = Path(__file__).parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# ─── Page configuration ───────────────────────────────────────────────────────
st.set_page_config(
    page_title="METROPULSE | Urban Mobility Intelligence",
    page_icon="🚇",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get Help":     "https://tfl.gov.uk/",
        "About":        "METROPULSE — Urban Mobility Intelligence Platform\nDataNova Global Data-thon 2026",
    },
)

# ─── Global Styling ───────────────────────────────────────────────────────────
st.markdown("""
<style>
/* ── Core palette ───────────────────────────────────── */
:root {
  --bg-primary:    #0a0f1e;
  --bg-secondary:  #111827;
  --bg-card:       #1a2235;
  --accent-blue:   #3b82f6;
  --accent-cyan:   #06b6d4;
  --accent-green:  #10b981;
  --accent-amber:  #f59e0b;
  --accent-red:    #ef4444;
  --text-primary:  #f1f5f9;
  --text-secondary:#94a3b8;
  --border-color:  #1e3a5f;
}

/* ── App background ─────────────────────────────────── */
.stApp { background-color: var(--bg-primary); color: var(--text-primary); }
[data-testid="stSidebar"] { background-color: var(--bg-secondary) !important; }
[data-testid="stSidebar"] .stMarkdown p { color: var(--text-secondary); }

/* ── Metric cards ───────────────────────────────────── */
[data-testid="metric-container"] {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 1rem !important;
  box-shadow: 0 4px 6px rgba(0,0,0,0.3);
}
[data-testid="metric-container"] [data-testid="stMetricLabel"] {
  color: var(--text-secondary) !important; font-size: 0.75rem !important;
  text-transform: uppercase; letter-spacing: 0.08em;
}
[data-testid="metric-container"] [data-testid="stMetricValue"] {
  color: var(--accent-blue) !important; font-size: 1.8rem !important; font-weight: 700;
}

/* ── Headers ────────────────────────────────────────── */
h1, h2, h3 { color: var(--text-primary) !important; }
h1 { font-size: 2rem !important; font-weight: 800; letter-spacing: -0.02em; }

/* ── Tabs ───────────────────────────────────────────── */
[data-testid="stTab"] { background: var(--bg-card); border-radius: 8px; }
.stTabs [data-baseweb="tab-list"] { background-color: var(--bg-secondary); border-radius: 8px; }
.stTabs [aria-selected="true"] { background-color: var(--accent-blue) !important; color: white !important; }

/* ── Selectboxes / inputs ───────────────────────────── */
.stSelectbox > div > div { background: var(--bg-card) !important; border-color: var(--border-color) !important; color: var(--text-primary) !important; }
.stMultiSelect > div > div { background: var(--bg-card) !important; }

/* ── DataFrames ─────────────────────────────────────── */
.stDataFrame { border: 1px solid var(--border-color); border-radius: 8px; }

/* ── Divider ────────────────────────────────────────── */
hr { border-color: var(--border-color); }

/* ── Custom brand header ────────────────────────────── */
.brand-header {
  background: linear-gradient(135deg, #0f2167 0%, #1a3a7c 50%, #0a1930 100%);
  border-radius: 16px; padding: 2rem 2.5rem; margin-bottom: 1.5rem;
  border: 1px solid #1e3a5f;
  box-shadow: 0 8px 32px rgba(0,0,0,0.4);
}
.brand-title {
  font-size: 2.4rem; font-weight: 900; letter-spacing: -0.03em;
  background: linear-gradient(90deg, #60a5fa, #06b6d4, #3b82f6);
  -webkit-background-clip: text; -webkit-text-fill-color: transparent;
  margin: 0;
}
.brand-subtitle { color: #94a3b8; font-size: 0.95rem; margin-top: 0.3rem; }
.badge {
  display: inline-block; padding: 0.25rem 0.75rem;
  border-radius: 999px; font-size: 0.7rem; font-weight: 600;
  letter-spacing: 0.05em; text-transform: uppercase;
}
.badge-blue  { background: rgba(59,130,246,0.2); color: #93c5fd; border: 1px solid rgba(59,130,246,0.3); }
.badge-green { background: rgba(16,185,129,0.2); color: #6ee7b7; border: 1px solid rgba(16,185,129,0.3); }
.badge-amber { background: rgba(245,158,11,0.2); color: #fcd34d; border: 1px solid rgba(245,158,11,0.3); }
</style>
""", unsafe_allow_html=True)

# ─── Sidebar branding ─────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="text-align:center; padding: 1rem 0;">
      <div style="font-size:2.5rem;">🚇</div>
      <div style="font-size:1.3rem; font-weight:800; color:#60a5fa; letter-spacing:-0.02em;">METROPULSE</div>
      <div style="font-size:0.7rem; color:#64748b; text-transform:uppercase; letter-spacing:0.1em;">
        Urban Mobility Intelligence
      </div>
    </div>
    <hr style="border-color:#1e3a5f; margin:0.5rem 0;">
    """, unsafe_allow_html=True)

    st.markdown("**Navigation**")
    st.info("Use the page list above to navigate between sections.")

    st.markdown("---")
    st.markdown("""
    <div style="font-size:0.7rem; color:#475569; text-align:center;">
      DataNova Global Data-thon 2026<br>
      Problem DN-DS-01<br>
      TfL NUMBAT Dataset 2023–2025<br>
      <span style="color:#3b82f6;">London Underground Analysis</span>
    </div>
    """, unsafe_allow_html=True)

# ─── Home page content ────────────────────────────────────────────────────────
st.markdown("""
<div class="brand-header">
  <div class="brand-title">🚇 METROPULSE</div>
  <div class="brand-subtitle">Urban Mobility Intelligence Platform — London Underground Analysis</div>
  <div style="margin-top:1rem;">
    <span class="badge badge-blue">DataNova 2026</span>&nbsp;
    <span class="badge badge-green">TfL NUMBAT 2023–2025</span>&nbsp;
    <span class="badge badge-amber">DN-DS-01</span>
  </div>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns([2, 1])
with col1:
    st.markdown("""
    ## Welcome to METROPULSE

    METROPULSE is an end-to-end Urban Mobility Intelligence Platform built on
    **TfL NUMBAT** (Network Usage Model Based Analysis Tool) datasets for
    London Underground passenger demand from **2023, 2024, and 2025**.

    ### Platform Capabilities
    - 📊 **Passenger Demand Analysis** — Station & line-level rankings, temporal profiles
    - 🔥 **Congestion Intelligence** — Load-per-train, peak detection, hotspot mapping
    - 🗺️ **Geospatial Analytics** — Interactive maps, demand heatmaps, spatial clustering
    - 🤖 **Machine Learning** — Demand forecasting, congestion classification, station clustering
    - 🔧 **Route Optimization** — Network analysis, bottleneck detection, service scenarios
    - 📁 **Data Explorer** — Filter, search, and download processed datasets

    ### Navigate using the sidebar pages ↑
    """)

with col2:
    st.markdown("""
    ### Quick Facts
    """)
    st.metric("Years Covered", "2023 · 2024 · 2025")
    st.metric("Day Types", "MON · TWT · FRI · SAT · SUN")
    st.metric("Source Files", "15 Excel Workbooks")
    st.metric("LU Lines", "10 Underground Lines")

st.markdown("---")
st.markdown("""
<div style="font-size:0.8rem; color:#475569; text-align:center;">
  <strong>Data Source:</strong> Transport for London (TfL) NUMBAT outputs · 
  <strong>Analysis Period:</strong> Typical operating day profiles 2023–2025 · 
  <strong>Mode:</strong> London Underground (LU) only
</div>
""", unsafe_allow_html=True)

