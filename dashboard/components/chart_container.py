"""
METROPULSE Chart Container Component
Wraps Plotly visualizations in styled dark cards with lineage badges and analytical takeaways.
"""
import streamlit as st
import plotly.graph_objects as go
from typing import Optional


def render_chart_container(
    fig: go.Figure,
    title: Optional[str] = None,
    subtitle: Optional[str] = None,
    lineage: str = "OBSERVED",
    takeaway: Optional[str] = None,
    height: int = 440,
):
    """
    Render a Plotly figure inside a styled card.

    Parameters
    ----------
    fig : go.Figure
        Plotly figure to render.
    title : str, optional
        Title of the visualization.
    subtitle : str, optional
        Subheading or data source note.
    lineage : str
        Lineage badge ('OBSERVED', 'DERIVED', 'PREDICTED', 'SIMULATED').
    takeaway : str, optional
        Analytical takeaway highlighted below the chart.
    height : int
        Height in pixels.
    """
    badge_class = {
        "OBSERVED": "badge-observed",
        "DERIVED": "badge-derived",
        "PREDICTED": "badge-predicted",
        "SIMULATED": "badge-simulated",
    }.get(lineage.upper(), "badge-external")

    # Ensure dark styling on the figure
    fig.update_layout(
        paper_bgcolor="#0D1422",
        plot_bgcolor="#080D17",
        font=dict(color="#F8FAFC", family="'Inter', sans-serif", size=12),
        margin=dict(l=45, r=20, t=30, b=40),
        height=height,
    )
    fig.update_xaxes(gridcolor="#172338", linecolor="#1E293B", tickfont=dict(color="#94A3B8"))
    fig.update_yaxes(gridcolor="#172338", linecolor="#1E293B", tickfont=dict(color="#94A3B8"))

    if title:
        header_html = f"""
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
            <div>
                <span style="font-weight: 700; font-size: 15px; color: #F8FAFC;">{title}</span>
                {f'<div style="font-size: 12px; color: #94A3B8;">{subtitle}</div>' if subtitle else ''}
            </div>
            <span class="badge {badge_class}">{lineage.upper()}</span>
        </div>
        """
        st.markdown(header_html, unsafe_allow_html=True)

    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    if takeaway:
        takeaway_html = f"""
        <div class="takeaway-box">
            <span class="takeaway-icon">💡</span>
            <span><strong>Key Finding:</strong> {takeaway}</span>
        </div>
        """
        st.markdown(takeaway_html, unsafe_allow_html=True)
