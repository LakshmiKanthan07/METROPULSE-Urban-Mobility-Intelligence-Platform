"""
METROPULSE Metric Card Component
Renders executive KPI cards with data lineage badges, units, tooltips, and strict missing value handling.
Never fabricates values or substitutes missing records with arbitrary zeros.
"""
import streamlit as st
import pandas as pd
from typing import Optional, Union


def render_metric_card(
    title: str,
    value: Optional[Union[str, int, float]],
    unit: str = "",
    subtitle: Optional[str] = None,
    change: Optional[Union[str, float]] = None,
    change_period: Optional[str] = None,
    status: str = "OBSERVED",
    tooltip: Optional[str] = None,
    missing_reason: Optional[str] = None,
):
    """
    Render a styled dark KPI card.

    Parameters
    ----------
    title : str
        Short label of the metric.
    value : str, int, float, or None
        Numerical or formatted string value. If None/NaN, displays graceful missing state.
    unit : str
        Unit suffix (e.g. "passengers", "tph", "%").
    subtitle : str, optional
        Contextual explanation or benchmark.
    change : float or str, optional
        Percentage or absolute delta. Omitted if None.
    change_period : str, optional
        Context for change (e.g. "vs 2024").
    status : str
        Lineage tag: 'OBSERVED', 'DERIVED', 'PREDICTED', 'SIMULATED', 'UNAVAILABLE', 'EXTERNAL_REQUIRED'.
    tooltip : str, optional
        Tooltip explanation.
    missing_reason : str, optional
        Reason why metric is unavailable if value is None.
    """
    # Determine badge class
    status_upper = status.upper()
    if status_upper == "OBSERVED":
        badge_html = '<span class="badge badge-observed">● OBSERVED</span>'
    elif status_upper == "DERIVED":
        badge_html = '<span class="badge badge-derived">◆ DERIVED</span>'
    elif status_upper == "PREDICTED":
        badge_html = '<span class="badge badge-predicted">▲ PREDICTED</span>'
    elif status_upper == "SIMULATED":
        badge_html = '<span class="badge badge-simulated">◈ SIMULATED</span>'
    elif status_upper in ("UNAVAILABLE", "EXTERNAL_REQUIRED"):
        badge_html = '<span class="badge badge-unavailable">✕ DATA NOT PROVIDED</span>'
    else:
        badge_html = f'<span class="badge badge-external">{status}</span>'

    # Check for missing / unavailable data
    is_missing = False
    if value is None:
        is_missing = True
    elif isinstance(value, (int, float)) and pd.isna(value):
        is_missing = True
    elif str(value).strip().upper() in ("N/A", "NONE", "NAN", "NULL", "DATA NOT PROVIDED", "REQUIRES EXTERNAL DATA"):
        is_missing = True

    if is_missing or status_upper in ("UNAVAILABLE", "EXTERNAL_REQUIRED"):
        val_display = '<span style="color: #64748B; font-size: 20px;">[DATA NOT PROVIDED]</span>'
        sub_text = missing_reason or subtitle or "Metric requires external data source not present in NUMBAT."
        delta_html = ""
    else:
        if isinstance(value, float):
            val_display = f"{value:,.1f}" if value % 1 != 0 else f"{int(value):,}"
        elif isinstance(value, int):
            val_display = f"{value:,}"
        else:
            val_display = str(value)

        if unit:
            val_display += f'<span class="kpi-unit">{unit}</span>'

        delta_html = ""
        if change is not None:
            if isinstance(change, (int, float)):
                if change > 0:
                    delta_html = f'<span class="kpi-delta-up">▲ +{change:.1f}%</span>'
                elif change < 0:
                    delta_html = f'<span class="kpi-delta-down">▼ {change:.1f}%</span>'
                else:
                    delta_html = '<span style="color: #94A3B8;">0.0%</span>'
            else:
                delta_html = f'<span style="color: #94A3B8;">{change}</span>'

            if change_period:
                delta_html += f' <span style="color: #64748B; font-size: 11px;">{change_period}</span>'

        sub_text = subtitle or ""

    tooltip_attr = f'title="{tooltip}"' if tooltip else ""

    card_html = f"""
    <div class="kpi-container" {tooltip_attr}>
        <div class="kpi-title">
            <span>{title}</span>
            {badge_html}
        </div>
        <div class="kpi-value">{val_display}</div>
        <div class="kpi-subtitle">
            {delta_html}
            <span>{sub_text}</span>
        </div>
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)
