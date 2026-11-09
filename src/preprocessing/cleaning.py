"""
METROPULSE — Data Cleaning
Applies cleaning operations after standardisation.
"""
import logging

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


def clean_common(df: pd.DataFrame) -> pd.DataFrame:
    """
    Apply common cleaning steps applicable to all datasets:
    - Strip whitespace from string columns
    - Remove all-NaN rows
    - Clip negative passenger counts to 0 (after logging)
    - Drop the NUMBAT summary 'Total' rows that are NaN in key identifiers
    """
    df = df.copy()

    # Strip whitespace from object columns
    str_cols = df.select_dtypes(include="object").columns
    for c in str_cols:
        df[c] = df[c].astype(str).str.strip()
        # Treat 'nan' strings as NaN
        df[c] = df[c].replace("nan", np.nan)

    # Remove rows where ALL non-metadata columns are null
    meta = ["year", "day_type", "source_file"]
    data_cols = [c for c in df.columns if c not in meta]
    df = df.dropna(subset=data_cols, how="all")

    # Clip tiny negative values (rounding artefacts) to 0, log large negatives
    for col in ["total", "early", "am_peak", "midday", "pm_peak",
                "evening", "late", "passengers"]:
        if col in df.columns:
            neg_mask = df[col] < 0
            n_neg = neg_mask.sum()
            if n_neg > 0:
                logger.warning(
                    "Column '%s': %d negative values — clipping to 0", col, n_neg
                )
                df.loc[neg_mask, col] = 0.0

    return df.reset_index(drop=True)


def normalise_direction(df: pd.DataFrame) -> pd.DataFrame:
    """
    Standardise direction codes to uppercase 2-letter codes:
    NB, SB, EB, WB, IB, OB.
    """
    if "direction" not in df.columns:
        return df
    df = df.copy()
    df["direction"] = df["direction"].astype(str).str.strip().str.upper()
    return df


def add_day_type_label(df: pd.DataFrame) -> pd.DataFrame:
    """Add human-readable day_type_label column."""
    from src.config.settings import DAY_TYPE_MAP
    if "day_type" not in df.columns:
        return df
    df = df.copy()
    df["day_type_label"] = df["day_type"].map(DAY_TYPE_MAP).fillna(df["day_type"])
    return df


def add_period_label(df: pd.DataFrame) -> pd.DataFrame:
    """
    Convert time_interval '0500-0515' into period label
    (Early, AM Peak, Midday, PM Peak, Evening, Late).
    Uses fast dict lookup for speed.
    """
    if "time_interval" not in df.columns:
        return df

    unique_intervals = df["time_interval"].dropna().unique()
    label_map = {}
    for ti in unique_intervals:
        try:
            start = int(str(ti).split("-")[0])
            if start < 630:
                label_map[ti] = "Early"
            elif start < 930:
                label_map[ti] = "AM Peak"
            elif start < 1600:
                label_map[ti] = "Midday"
            elif start < 1900:
                label_map[ti] = "PM Peak"
            elif start < 2200:
                label_map[ti] = "Evening"
            else:
                label_map[ti] = "Late"
        except Exception:
            label_map[ti] = "Unknown"

    df = df.copy()
    df["period"] = df["time_interval"].map(label_map).fillna("Unknown")
    return df


def add_start_minute(df: pd.DataFrame) -> pd.DataFrame:
    """Add start_minute column (minutes since midnight) from time_interval.
    Uses fast dict lookup for speed.
    """
    if "time_interval" not in df.columns:
        return df

    unique_intervals = df["time_interval"].dropna().unique()
    minute_map = {}
    for ti in unique_intervals:
        try:
            start = str(ti).split("-")[0]
            minute_map[ti] = int(start[:2]) * 60 + int(start[2:])
        except Exception:
            minute_map[ti] = -1

    df = df.copy()
    df["start_minute"] = df["time_interval"].map(minute_map).fillna(-1).astype(int)
    return df

