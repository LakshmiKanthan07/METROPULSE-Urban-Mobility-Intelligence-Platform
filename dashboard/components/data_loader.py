"""
METROPULSE Dashboard — Shared Data Loader with Caching
Avoids re-reading Excel files during dashboard interaction.
"""
import sys
from pathlib import Path
import streamlit as st
import pandas as pd
import numpy as np

ROOT = Path(__file__).parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.config.settings import DATA_CSV, DATA_PARQUET, DATA_BI

# ─── TfL brand colours ────────────────────────────────────────────────────────
LINE_COLOURS = {
    "Bakerloo":           "#B36305",
    "Central":            "#E32017",
    "District":           "#00782A",
    "H&C and Circle":     "#F3A9BB",
    "Jubilee":            "#A0A5A9",
    "Metropolitan":       "#9B0056",
    "Northern":           "#000000",
    "Piccadilly":         "#003688",
    "Victoria":           "#0098D4",
    "Waterloo & City":    "#95CDBA",
    "Circle":             "#FFD300",
    "Hammersmith & City": "#F3A9BB",
    # Fallback
    "default":            "#3b82f6",
}

LINE_CODE_TO_NAME = {
    "BAK": "Bakerloo",
    "CEN": "Central",
    "DIS": "District",
    "HAM": "H&C and Circle",
    "JUB": "Jubilee",
    "MET": "Metropolitan",
    "NOR": "Northern",
    "PIC": "Piccadilly",
    "VIC": "Victoria",
    "WAC": "Waterloo & City",
}


@st.cache_data(show_spinner="Loading data...")
def load(name: str) -> pd.DataFrame:
    """Load a processed parquet dataset with Streamlit caching."""
    parquet_path = DATA_PARQUET / f"{name}.parquet"
    csv_path     = DATA_CSV / f"{name}.csv"
    if parquet_path.exists():
        return pd.read_parquet(parquet_path, engine="pyarrow")
    elif csv_path.exists():
        return pd.read_csv(csv_path)
    else:
        return pd.DataFrame()


@st.cache_data(show_spinner=False)
def load_csv(name: str) -> pd.DataFrame:
    """Load a CSV from data/processed/csv/."""
    path = DATA_CSV / f"{name}.csv"
    if path.exists():
        return pd.read_csv(path)
    return pd.DataFrame()


@st.cache_data(show_spinner=False)
def load_bi(name: str) -> pd.DataFrame:
    """Load a BI export CSV."""
    path = DATA_BI / f"{name}.csv"
    if path.exists():
        return pd.read_csv(path)
    return pd.DataFrame()


@st.cache_data(show_spinner=False)
def load_coords() -> pd.DataFrame:
    """Load station coordinates."""
    from src.config.settings import DATA_EXTERNAL
    path = DATA_EXTERNAL / "lu_station_coords.csv"
    if path.exists():
        return pd.read_csv(path)
    return pd.DataFrame()


def get_line_colour(line_name: str) -> str:
    """Return TfL brand colour for a line."""
    for k, v in LINE_COLOURS.items():
        if k.lower() in str(line_name).lower():
            return v
    return LINE_COLOURS["default"]


def format_number(n, suffix="") -> str:
    """Format large numbers compactly."""
    if pd.isna(n):
        return "N/A"
    n = float(n)
    if abs(n) >= 1_000_000:
        return f"{n/1_000_000:.1f}M{suffix}"
    elif abs(n) >= 1_000:
        return f"{n/1_000:.0f}K{suffix}"
    return f"{n:.0f}{suffix}"


def apply_common_filters(df: pd.DataFrame,
                          year_col: str = "year",
                          day_col: str = "day_type",
                          line_col: str = "line") -> pd.DataFrame:
    """Apply sidebar year/day_type/line filters."""
    if df.empty:
        return df

    if year_col in df.columns:
        years = sorted(df[year_col].dropna().unique())
        sel_yr = st.sidebar.multiselect("Year", years, default=years, key=f"yr_{year_col}")
        if sel_yr:
            df = df[df[year_col].isin(sel_yr)]

    if day_col in df.columns:
        days = sorted(df[day_col].dropna().unique())
        sel_day = st.sidebar.multiselect("Day Type", days, default=days, key=f"day_{day_col}")
        if sel_day:
            df = df[df[day_col].isin(sel_day)]

    return df


# ─── Plotly theme ─────────────────────────────────────────────────────────────
PLOTLY_TEMPLATE = {
    "layout": {
        "paper_bgcolor": "#0a0f1e",
        "plot_bgcolor":  "#111827",
        "font":          {"color": "#f1f5f9", "family": "Inter, sans-serif"},
        "xaxis": {"gridcolor": "#1e3a5f", "linecolor": "#1e3a5f"},
        "yaxis": {"gridcolor": "#1e3a5f", "linecolor": "#1e3a5f"},
        "colorway": ["#3b82f6","#06b6d4","#10b981","#f59e0b","#ef4444",
                     "#8b5cf6","#ec4899","#14b8a6","#f97316","#a855f7"],
    }
}

