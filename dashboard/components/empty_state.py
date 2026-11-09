"""
METROPULSE Empty State Component
Displays structured placeholders when data is filtered out, unavailable, or missing.
"""
import streamlit as st
from typing import Optional


def render_empty_state(
    title: str = "No Data Available",
    message: str = "No records match the current filter selection.",
    status: str = "INSUFFICIENT DATA",
    suggestion: Optional[str] = "Try widening the selected years, lines, or time intervals in the filter panel.",
    icon: str = "🔍",
):
    """
    Render a clean empty state card.
    """
    html = f"""
    <div class="empty-state-card">
        <div style="font-size: 32px; margin-bottom: 12px;">{icon}</div>
        <div class="empty-state-title">{title}</div>
        <div class="empty-state-desc">{message}</div>
        {f'<div style="font-size: 12px; color: #3B82F6; margin-top: 10px;">💡 {suggestion}</div>' if suggestion else ''}
        <div style="margin-top: 12px;">
            <span class="badge badge-unavailable">{status}</span>
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)
