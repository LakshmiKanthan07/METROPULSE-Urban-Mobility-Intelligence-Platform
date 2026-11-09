"""
METROPULSE Data Table Component
Displays styled, interactive dataframes with missing value handling, column formatting, and CSV export.
"""
import streamlit as st
import pandas as pd
from typing import Optional, List


def render_data_table(
    df: pd.DataFrame,
    title: Optional[str] = None,
    download_filename: str = "metropulse_export.csv",
    display_cols: Optional[List[str]] = None,
    max_rows: int = 100,
):
    """
    Render a clean data table with null indicators and CSV export.
    """
    if df is None or df.empty:
        st.info("No data available to display in table.")
        return

    target_df = df[display_cols] if display_cols else df.copy()

    # Format numeric floats and nulls for presentation
    preview_df = target_df.head(max_rows).copy()

    header_cols = st.columns([4, 1])
    with header_cols[0]:
        if title:
            st.markdown(f"**{title}** <span style='color: #64748B; font-size: 12px;'>({len(df):,} total records)</span>", unsafe_allow_html=True)
    with header_cols[1]:
        csv_bytes = target_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Export CSV",
            data=csv_bytes,
            file_name=download_filename,
            mime="text/csv",
            use_container_width=True,
        )

    # Style missing values clearly
    st.dataframe(
        preview_df.fillna("—"),
        use_container_width=True,
        height=min(400, 38 + len(preview_df) * 35),
    )

