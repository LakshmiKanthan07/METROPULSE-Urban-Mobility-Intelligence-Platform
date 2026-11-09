"""
METROPULSE — Data Standardization
Normalises column names, data types, time intervals and values
across all years and day types.
"""
import logging
import re
from typing import Union

import numpy as np
import pandas as pd

from src.config.settings import PERIOD_COL_MAP, DAY_TYPE_MAP

logger = logging.getLogger(__name__)

# ─── Time-interval column pattern: '0500-0515', '0515-0530', etc.
_TIME_INTERVAL_RE = re.compile(r"^\d{4}-\d{4}$")

# ─── Period aggregates (stripped) ────────────────────────────────────────────
_PERIOD_RENAMES = {k.strip(): v for k, v in PERIOD_COL_MAP.items()}


def standardise_link_loads(df: pd.DataFrame) -> pd.DataFrame:
    """
    Standardise the Link_Loads / Link_Frequencies worksheets.
    Both share an identical structure.
    """
    df = df.copy()
    df = _rename_meta_cols(df, {
        "Link":         "link",
        "Line":         "line",
        "Dir":          "direction",
        "Order":        "order",
        "From NLC":     "from_nlc",
        "From ASC":     "from_asc",
        "From Station": "from_station",
        "To NLC":       "to_nlc",
        "To ASC":       "to_asc",
        "To Station":   "to_station",
        "Total":        "total",
    })
    df = _rename_period_cols(df)
    df = _melt_time_intervals(df, id_cols=[
        "link", "line", "direction", "order",
        "from_nlc", "from_asc", "from_station",
        "to_nlc",   "to_asc",   "to_station",
        "total", "early", "am_peak", "midday", "pm_peak", "evening", "late",
        "year", "day_type", "source_file",
    ])
    df = _cast_numerics(df, ["total", "early", "am_peak", "midday",
                              "pm_peak", "evening", "late", "passengers"])
    df = _extract_line_code(df)
    return df


def standardise_line_boarders(df: pd.DataFrame) -> pd.DataFrame:
    """Standardise Line_Boarders worksheet."""
    df = df.copy()
    df = _rename_meta_cols(df, {
        "Mode":      "mode",
        "Line Code": "line_code",
        "Line Name": "line_name",
        "Total":     "total",
    })
    df = _rename_period_cols(df)
    df = _melt_time_intervals(df, id_cols=[
        "mode", "line_code", "line_name",
        "total", "early", "am_peak", "midday", "pm_peak", "evening", "late",
        "year", "day_type", "source_file",
    ])
    df = _cast_numerics(df, ["total", "early", "am_peak", "midday",
                              "pm_peak", "evening", "late", "passengers"])
    return df


def standardise_station_entries_exits(df: pd.DataFrame) -> pd.DataFrame:
    """Standardise Station_Entries and Station_Exits worksheets (same schema)."""
    df = df.copy()
    df.columns = [str(c) for c in df.columns]
    df = _rename_meta_cols(df, {
        "NLC":       "nlc",
        "ASC":       "asc",
        "Station":   "station",
        "Fare Zone": "fare_zone",
        "Total":     "total",
    })
    df = _rename_period_cols(df)
    df = _melt_time_intervals(df, id_cols=[
        "nlc", "asc", "station", "fare_zone",
        "total", "early", "am_peak", "midday", "pm_peak", "evening", "late",
        "year", "day_type", "source_file",
    ])
    df = _cast_numerics(df, ["nlc", "total", "early", "am_peak", "midday",
                              "pm_peak", "evening", "late", "passengers"])
    return df


def standardise_station_boarders_alighters(df: pd.DataFrame) -> pd.DataFrame:
    """Standardise Station_Boarders and Station_Alighters worksheets."""
    df = df.copy()
    df.columns = [str(c) for c in df.columns]
    df = _rename_meta_cols(df, {
        "ID":       "id",
        "NLC":      "nlc",
        "ASC":      "asc",
        "Station":  "station",
        "Mode":     "mode",
        "Line":     "line",
        "Dir":      "direction",
        "Platform": "platform",
        "Total":    "total",
    })
    df = _rename_period_cols(df)
    df = _melt_time_intervals(df, id_cols=[
        "id", "nlc", "asc", "station", "mode", "line", "direction", "platform",
        "total", "early", "am_peak", "midday", "pm_peak", "evening", "late",
        "year", "day_type", "source_file",
    ])
    df = _cast_numerics(df, ["nlc", "total", "early", "am_peak", "midday",
                              "pm_peak", "evening", "late", "passengers"])
    return df


def standardise_station_flows(df: pd.DataFrame) -> pd.DataFrame:
    """Standardise Station_Flows worksheet."""
    df = df.copy()
    df.columns = [str(c) for c in df.columns]
    df = _rename_meta_cols(df, {
        "ID":           "id",
        "Complex NLC":  "complex_nlc",
        "From NLC":     "from_nlc",
        "From ASC":     "from_asc",
        "From Station": "from_station",
        "From Node":    "from_node",
        "To NLC":       "to_nlc",
        "To ASC":       "to_asc",
        "To Station":   "to_station",
        "To Node":      "to_node",
        "Movement":     "movement",
        "Total":        "total",
    })
    df = _rename_period_cols(df)
    df = _melt_time_intervals(df, id_cols=[
        "id", "complex_nlc", "from_nlc", "from_asc", "from_station",
        "from_node", "to_nlc", "to_asc", "to_station", "to_node",
        "movement", "total", "early", "am_peak", "midday", "pm_peak",
        "evening", "late", "year", "day_type", "source_file",
    ])
    df = _cast_numerics(df, ["from_nlc", "to_nlc", "complex_nlc",
                              "total", "passengers"])
    return df


# ─── Internal helpers ─────────────────────────────────────────────────────────

def _rename_meta_cols(df: pd.DataFrame, rename_map: dict) -> pd.DataFrame:
    """
    Case-insensitive rename of metadata columns.
    Skips entries where source column is not found.
    """
    df = df.copy()
    df.columns = [str(c).strip() for c in df.columns]
    df = df.loc[:, ~df.columns.duplicated(keep="first")]
    lower_to_actual = {c.lower(): c for c in df.columns}
    actual_rename = {}
    for src, tgt in rename_map.items():
        actual = lower_to_actual.get(src.strip().lower())
        if actual:
            actual_rename[actual] = tgt
    res = df.rename(columns=actual_rename)
    return res.loc[:, ~res.columns.duplicated(keep="first")]


def _rename_period_cols(df: pd.DataFrame) -> pd.DataFrame:
    """Rename stripped-whitespace period summary columns.
    Also converts all column names to strings first (handles int/float col names
    from pandas concat of multi-file DataFrames).
    """
    # Normalise all column names to strings
    df = df.copy()
    df.columns = [str(c).strip() for c in df.columns]
    df = df.loc[:, ~df.columns.duplicated(keep="first")]
    rename = {}
    for col in df.columns:
        if col in _PERIOD_RENAMES:
            rename[col] = _PERIOD_RENAMES[col]
    res = df.rename(columns=rename)
    return res.loc[:, ~res.columns.duplicated(keep="first")]


def _melt_time_intervals(df: pd.DataFrame, id_cols: list[str]) -> pd.DataFrame:
    """
    Melt 15-minute interval columns (e.g. '0500-0515') into long form.
    New columns: time_interval (str), passengers (float).
    id_cols that are absent from df are silently skipped.
    """
    # Ensure all column names are strings first and deduplicated
    df = df.copy()
    df.columns = [str(c).strip() for c in df.columns]
    df = df.loc[:, ~df.columns.duplicated(keep="first")]

    # Preserve order of id_cols while removing duplicates
    present_id_cols = list(dict.fromkeys([c for c in id_cols if c in df.columns]))
    interval_cols = [
        c for c in df.columns
        if _TIME_INTERVAL_RE.match(str(c))
    ]
    if not interval_cols:
        return df  # no intervals to melt

    # Select only necessary columns before melting and deduplicate
    df_subset = df[present_id_cols + interval_cols].copy()
    df_subset = df_subset.loc[:, ~df_subset.columns.duplicated(keep="first")]

    # Ensure all interval columns are float
    for ic in interval_cols:
        if ic in df_subset.columns:
            df_subset[ic] = pd.to_numeric(df_subset[ic], errors="coerce")

    melted = df_subset.melt(
        id_vars=present_id_cols,
        value_vars=interval_cols,
        var_name="time_interval",
        value_name="passengers",
    )
    return melted


def _cast_numerics(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    """Coerce specified columns to numeric, filling errors with NaN."""
    for col in cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def _extract_line_code(df: pd.DataFrame) -> pd.DataFrame:
    """
    For Link_Loads / Link_Frequencies: extract line_code from the link column
    if not already present.
    Format: FROM_LINECD_DIR>TO_LINECD_DIR@LINECD
    """
    if "line_code" in df.columns:
        return df
    if "link" not in df.columns:
        return df

    def _code(val: str) -> str:
        try:
            return val.split("@")[-1].split("_")[0].upper()
        except Exception:
            return ""

    df = df.copy()
    df["line_code"] = df["link"].astype(str).apply(_code)
    return df


def parse_time_interval_to_minutes(interval: str) -> int:
    """
    Convert '0500-0515' → minutes since midnight (start of interval).
    Returns -1 if parsing fails.
    """
    try:
        start = interval.split("-")[0]
        hours = int(start[:2])
        mins  = int(start[2:])
        return hours * 60 + mins
    except Exception:
        return -1
