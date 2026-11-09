"""
METROPULSE Filter Bar Component
Provides consistent, lightweight filtering across pages without slowing down execution.
"""
import streamlit as st
import pandas as pd
from typing import Tuple, List, Optional


def render_filter_bar(
    df: pd.DataFrame,
    year_col: str = "year",
    day_col: str = "day_type",
    line_col: Optional[str] = "line",
    key_prefix: str = "",
) -> Tuple[pd.DataFrame, dict]:
    """
    Render horizontal filter widgets and return filtered DataFrame plus active filter dict.
    """
    if df is None or df.empty:
        return df, {}

    active_filters = {}
    filtered_df = df

    # Available options
    years = sorted(df[year_col].dropna().unique().tolist()) if year_col in df.columns else []
    day_types = sorted(df[day_col].dropna().unique().tolist()) if day_col in df.columns else []
    lines = sorted(df[line_col].dropna().unique().tolist()) if line_col and line_col in df.columns else []

    col_count = 1 + (1 if day_types else 0) + (1 if lines else 0)
    cols = st.columns(col_count)

    idx = 0
    if years:
        with cols[idx]:
            sel_years = st.multiselect(
                "Filter Year",
                options=years,
                default=years,
                key=f"{key_prefix}_year_filter",
            )
            if sel_years:
                filtered_df = filtered_df[filtered_df[year_col].isin(sel_years)]
                active_filters["Year"] = sel_years
        idx += 1

    if day_types:
        with cols[idx]:
            sel_days = st.multiselect(
                "Filter Day Type",
                options=day_types,
                default=day_types,
                key=f"{key_prefix}_day_filter",
            )
            if sel_days:
                filtered_df = filtered_df[filtered_df[day_col].isin(sel_days)]
                active_filters["Day"] = sel_days
        idx += 1

    if lines:
        with cols[idx]:
            sel_lines = st.multiselect(
                "Filter Line",
                options=lines,
                default=lines,
                key=f"{key_prefix}_line_filter",
            )
            if sel_lines:
                filtered_df = filtered_df[filtered_df[line_col].isin(sel_lines)]
                active_filters["Line"] = sel_lines
        idx += 1

    return filtered_df, active_filters

