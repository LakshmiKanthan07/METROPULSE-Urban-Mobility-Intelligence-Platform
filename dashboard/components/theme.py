"""
METROPULSE Enterprise Dark Theme & Design Tokens
Color Palette:
- Canvas: #080D17
- Card Surface: #0D1422
- Elevated Card / Hover: #111B2B
- Card Border: #172338 / #1E293B
- Accent Blue: #3B82F6
- Accent Cyan: #22D3EE
- Text Primary: #F8FAFC
- Text Secondary: #94A3B8
- Text Muted: #64748B
- Semantic: Green #10B981, Amber #F59E0B, Red #EF4444, Purple #8B5CF6
"""
import streamlit as st

LINEAGE_COLORS = {
    "OBSERVED": {"bg": "rgba(16, 185, 129, 0.15)", "text": "#10B981", "border": "#059669"},
    "DERIVED": {"bg": "rgba(34, 211, 238, 0.15)", "text": "#22D3EE", "border": "#0891B2"},
    "PREDICTED": {"bg": "rgba(139, 92, 246, 0.15)", "text": "#A78BFA", "border": "#7C3AED"},
    "SIMULATED": {"bg": "rgba(245, 158, 11, 0.15)", "text": "#FBBF24", "border": "#D97706"},
    "UNAVAILABLE": {"bg": "rgba(239, 68, 68, 0.15)", "text": "#F87171", "border": "#DC2626"},
    "EXTERNAL_REQUIRED": {"bg": "rgba(100, 116, 139, 0.2)", "text": "#CBD5E1", "border": "#475569"},
    "NOT_APPLICABLE": {"bg": "rgba(71, 85, 105, 0.2)", "text": "#94A3B8", "border": "#334155"},
}

PLOTLY_DARK_LAYOUT = {
    "paper_bgcolor": "#0D1422",
    "plot_bgcolor": "#080D17",
    "font": {"color": "#F8FAFC", "family": "'Inter', 'Segoe UI', -apple-system, sans-serif", "size": 12},
    "xaxis": {
        "gridcolor": "#172338",
        "linecolor": "#1E293B",
        "tickfont": {"color": "#94A3B8", "size": 11},
        "titlefont": {"color": "#F8FAFC", "size": 12},
    },
    "yaxis": {
        "gridcolor": "#172338",
        "linecolor": "#1E293B",
        "tickfont": {"color": "#94A3B8", "size": 11},
        "titlefont": {"color": "#F8FAFC", "size": 12},
    },
    "legend": {
        "bgcolor": "rgba(13, 20, 34, 0.8)",
        "bordercolor": "#172338",
        "borderwidth": 1,
        "font": {"color": "#F8FAFC"},
    },
    "margin": {"l": 50, "r": 20, "t": 40, "b": 40},
    "colorway": ["#3B82F6", "#22D3EE", "#10B981", "#F59E0B", "#EF4444", "#8B5CF6", "#EC4899", "#14B8A6"],
}


def apply_custom_css():
    """Inject premium dark command center styling across the application."""
    css = """
    <style>
    /* Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

    /* Global canvas */
    .stApp {
        background-color: #080D17 !important;
        color: #F8FAFC !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    }

    /* Streamlit top header / toolbar */
    header[data-testid="stHeader"] {
        background-color: rgba(8, 13, 23, 0.95) !important;
        backdrop-filter: blur(8px) !important;
        border-bottom: 1px solid #172338 !important;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #0A101D !important;
        border-right: 1px solid #172338 !important;
    }
    section[data-testid="stSidebar"] div.stRadio > label {
        color: #94A3B8 !important;
        font-weight: 500;
    }

    /* Typography overrides */
    h1, h2, h3, h4, h5, h6 {
        color: #F8FAFC !important;
        font-weight: 700 !important;
        letter-spacing: -0.02em !important;
    }
    p, span, label, div {
        color: #E2E8F0;
    }
    small, .text-muted {
        color: #94A3B8 !important;
    }

    /* Command Center Cards */
    .metro-card {
        background: #0D1422;
        border: 1px solid #172338;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 16px;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.35);
        transition: border-color 0.2s ease, transform 0.2s ease;
    }
    .metro-card:hover {
        border-color: #263852;
    }

    .metro-card-elevated {
        background: #111B2B;
        border: 1px solid #1E2D44;
        border-radius: 10px;
        padding: 22px;
        margin-bottom: 16px;
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.45);
    }

    /* Metric KPI Card */
    .kpi-container {
        background: #0D1422;
        border: 1px solid #172338;
        border-radius: 10px;
        padding: 16px 18px;
        position: relative;
        overflow: hidden;
        min-height: 110px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    .kpi-container::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 3px;
        background: linear-gradient(90deg, #3B82F6, #22D3EE);
    }
    .kpi-title {
        font-size: 11px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: #94A3B8;
        margin-bottom: 6px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .kpi-value {
        font-size: 26px;
        font-weight: 800;
        color: #F8FAFC;
        font-family: 'JetBrains Mono', monospace;
        line-height: 1.1;
    }
    .kpi-unit {
        font-size: 14px;
        font-weight: 500;
        color: #94A3B8;
        margin-left: 4px;
    }
    .kpi-subtitle {
        font-size: 12px;
        color: #64748B;
        margin-top: 6px;
        display: flex;
        align-items: center;
        gap: 6px;
    }
    .kpi-delta-up {
        color: #10B981;
        font-size: 12px;
        font-weight: 600;
    }
    .kpi-delta-down {
        color: #EF4444;
        font-size: 12px;
        font-weight: 600;
    }

    /* Lineage & Status Badges */
    .badge {
        display: inline-flex;
        align-items: center;
        gap: 4px;
        font-size: 10px;
        font-weight: 700;
        letter-spacing: 0.06em;
        text-transform: uppercase;
        padding: 2px 7px;
        border-radius: 4px;
        border: 1px solid transparent;
        line-height: 1.3;
    }
    .badge-observed {
        background: rgba(16, 185, 129, 0.15);
        color: #10B981;
        border-color: rgba(16, 185, 129, 0.35);
    }
    .badge-derived {
        background: rgba(34, 211, 238, 0.15);
        color: #22D3EE;
        border-color: rgba(34, 211, 238, 0.35);
    }
    .badge-predicted {
        background: rgba(139, 92, 246, 0.15);
        color: #C084FC;
        border-color: rgba(139, 92, 246, 0.35);
    }
    .badge-simulated {
        background: rgba(245, 158, 11, 0.15);
        color: #FBBF24;
        border-color: rgba(245, 158, 11, 0.35);
    }
    .badge-unavailable {
        background: rgba(239, 68, 68, 0.15);
        color: #F87171;
        border-color: rgba(239, 68, 68, 0.35);
    }
    .badge-external {
        background: rgba(100, 116, 139, 0.2);
        color: #94A3B8;
        border-color: rgba(100, 116, 139, 0.4);
    }

    /* Section Headers */
    .section-header-box {
        margin-top: 18px;
        margin-bottom: 12px;
        padding-bottom: 8px;
        border-bottom: 1px solid #172338;
        display: flex;
        justify-content: space-between;
        align-items: flex-end;
    }
    .section-title {
        font-size: 18px;
        font-weight: 700;
        color: #F8FAFC;
        letter-spacing: -0.01em;
        margin: 0;
    }
    .section-subtitle {
        font-size: 13px;
        color: #94A3B8;
        margin-top: 3px;
        margin-bottom: 0;
    }

    /* Analytical Takeaway Callout */
    .takeaway-box {
        background: #0A1322;
        border-left: 3px solid #3B82F6;
        border-radius: 0 6px 6px 0;
        padding: 10px 14px;
        margin-top: 10px;
        font-size: 13px;
        color: #CBD5E1;
        display: flex;
        align-items: flex-start;
        gap: 8px;
    }
    .takeaway-icon {
        color: #3B82F6;
        font-weight: bold;
        flex-shrink: 0;
    }

    /* Empty / Missing Data State */
    .empty-state-card {
        background: #0D1422;
        border: 1px dashed #1E2D44;
        border-radius: 10px;
        padding: 32px 24px;
        text-align: center;
        color: #94A3B8;
        margin: 16px 0;
    }
    .empty-state-title {
        font-size: 15px;
        font-weight: 600;
        color: #F8FAFC;
        margin-bottom: 6px;
    }
    .empty-state-desc {
        font-size: 13px;
        color: #64748B;
        max-width: 500px;
        margin: 0 auto;
    }

    /* Streamlit widgets overrides */
    div[data-baseweb="select"] > div {
        background-color: #0D1422 !important;
        border-color: #172338 !important;
        color: #F8FAFC !important;
    }
    div[data-baseweb="popover"] {
        background-color: #0D1422 !important;
    }
    div[data-baseweb="tab-list"] {
        background-color: #080D17 !important;
        border-bottom: 1px solid #172338 !important;
    }
    button[data-baseweb="tab"] {
        color: #94A3B8 !important;
        font-weight: 600 !important;
        border-radius: 6px 6px 0 0 !important;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        color: #3B82F6 !important;
        border-bottom: 2px solid #3B82F6 !important;
    }
    .stDownloadButton > button {
        background-color: #111B2B !important;
        color: #22D3EE !important;
        border: 1px solid #1E2D44 !important;
        border-radius: 6px !important;
        font-weight: 600 !important;
        transition: all 0.2s ease !important;
    }
    .stDownloadButton > button:hover {
        background-color: #16243A !important;
        border-color: #3B82F6 !important;
        color: #F8FAFC !important;
    }

    /* Scrollbars */
    ::-webkit-scrollbar {
        width: 6px;
        height: 6px;
    }
    ::-webkit-scrollbar-track {
        background: #080D17;
    }
    ::-webkit-scrollbar-thumb {
        background: #172338;
        border-radius: 3px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: #1E2D44;
    }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)
