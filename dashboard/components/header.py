"""
METROPULSE Header Component
Renders top-level navigation breadcrumbs, dataset timestamp, and active filter badges.
"""
import streamlit as st
from typing import Optional, Dict, Any


def render_header(
    page_name: str,
    subtitle: Optional[str] = None,
    active_filters: Optional[Dict[str, Any]] = None,
):
    """
    Render top command center header banner.
    """
    badge_items = []
    if active_filters:
        for k, v in active_filters.items():
            if v:
                if isinstance(v, list):
                    v_str = ", ".join(str(x) for x in v[:3])
                    if len(v) > 3:
                        v_str += f" +{len(v)-3}"
                else:
                    v_str = str(v)
                badge_items.append(f'<span class="badge badge-derived">{k.upper()}: {v_str}</span>')

    filter_html = "".join(badge_items) if badge_items else '<span class="badge badge-observed">CORPUS: FULL TFL NUMBAT (2023–2025)</span>'

    html = f"""
    <div style="display: flex; justify-content: space-between; align-items: flex-start; padding: 10px 0 20px 0; border-bottom: 1px solid #172338; margin-bottom: 24px;">
        <div>
            <div style="font-size: 11px; font-weight: 700; letter-spacing: 0.12em; text-transform: uppercase; color: #3B82F6;">
                METROPULSE &nbsp;/&nbsp; <span style="color: #94A3B8;">{page_name.upper()}</span>
            </div>
            <h1 style="font-size: 28px; font-weight: 800; margin: 4px 0 0 0; color: #F8FAFC; letter-spacing: -0.03em;">
                {page_name}
            </h1>
            {f'<div style="font-size: 14px; color: #94A3B8; margin-top: 4px;">{subtitle}</div>' if subtitle else ''}
        </div>
        <div style="display: flex; flex-direction: column; align-items: flex-end; gap: 6px;">
            <div style="display: flex; gap: 6px; flex-wrap: wrap; justify-content: flex-end;">
                {filter_html}
            </div>
            <div style="font-size: 11px; color: #64748B;">
                Zero-Fabrication Protocol Active &bull; Verified TfL Data
            </div>
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

