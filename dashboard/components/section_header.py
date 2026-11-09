"""
METROPULSE Section Header Component
Renders consistent, high-contrast section headers with subtitles and lineage indicators.
"""
import streamlit as st
from typing import Optional


def render_section_header(
    title: str,
    subtitle: Optional[str] = None,
    status: Optional[str] = None,
    icon: Optional[str] = None,
):
    """
    Render a clean dark section header.

    Parameters
    ----------
    title : str
        Main section title.
    subtitle : str, optional
        Descriptive contextual text.
    status : str, optional
        Status badge (e.g. 'OBSERVED', 'DERIVED', 'SIMULATION').
    icon : str, optional
        Icon emoji or symbol.
    """
    badge_html = ""
    if status:
        st_upper = status.upper()
        if st_upper == "OBSERVED":
            badge_html = '<span class="badge badge-observed">● OBSERVED</span>'
        elif st_upper == "DERIVED":
            badge_html = '<span class="badge badge-derived">◆ DERIVED</span>'
        elif st_upper == "PREDICTED":
            badge_html = '<span class="badge badge-predicted">▲ PREDICTED</span>'
        elif st_upper == "SIMULATED":
            badge_html = '<span class="badge badge-simulated">◈ SIMULATED SCENARIO</span>'
        elif st_upper in ("UNAVAILABLE", "EXTERNAL_REQUIRED"):
            badge_html = '<span class="badge badge-unavailable">✕ DATA NOT PROVIDED</span>'
        else:
            badge_html = f'<span class="badge badge-external">{status}</span>'

    icon_str = f"{icon} " if icon else ""

    header_html = f"""
    <div class="section-header-box">
        <div>
            <h3 class="section-title">{icon_str}{title}</h3>
            {f'<p class="section-subtitle">{subtitle}</p>' if subtitle else ''}
        </div>
        <div>
            {badge_html}
        </div>
    </div>
    """
    st.markdown(header_html, unsafe_allow_html=True)

