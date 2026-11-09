"""
METROPULSE — Mode Filter
Isolates London Underground records from multi-modal NUMBAT datasets.
"""
import logging
from typing import Optional

import pandas as pd

from src.config.settings import LU_MODE_CODE, LU_LINE_CODES, LU_ASC_SUFFIX

logger = logging.getLogger(__name__)

# ─── Sheets that contain an explicit Mode column ──────────────────────────────
MODE_COL_SHEETS = {"Station_Boarders", "Station_Alighters", "Line_Boarders"}

# ─── Sheets filtered by ASC suffix 'u' ───────────────────────────────────────
ASC_FILTER_SHEETS = {"Station_Entries", "Station_Exits"}

# ─── Sheets filtered by Line code membership ─────────────────────────────────
LINE_FILTER_SHEETS = {"Link_Loads", "Link_Frequencies"}

# ─── Station_Flows — LU inferred from From/To ASC codes ──────────────────────
FLOW_FILTER_SHEETS = {"Station_Flows"}


def filter_lu(df: pd.DataFrame, sheet_name: str) -> pd.DataFrame:
    """
    Apply London Underground filter appropriate for the given worksheet.

    Returns a filtered copy of df, never modifying the original.
    Records the number of rows retained vs discarded.
    """
    n_before = len(df)

    if sheet_name in MODE_COL_SHEETS:
        df = _filter_by_mode(df, sheet_name)
    elif sheet_name in ASC_FILTER_SHEETS:
        df = _filter_by_asc(df, sheet_name)
    elif sheet_name in LINE_FILTER_SHEETS:
        df = _filter_by_line(df, sheet_name)
    elif sheet_name in FLOW_FILTER_SHEETS:
        df = _filter_flows(df, sheet_name)
    else:
        logger.debug("No LU filter applied for sheet '%s'", sheet_name)
        return df.copy()

    n_after = len(df)
    logger.info(
        "LU filter [%s]: %d → %d rows retained (%.1f%%)",
        sheet_name, n_before, n_after,
        100 * n_after / max(n_before, 1),
    )
    return df.reset_index(drop=True)


def _filter_by_mode(df: pd.DataFrame, sheet_name: str) -> pd.DataFrame:
    """Keep rows where Mode == 'LU'."""
    mode_col = _find_col(df, ["Mode", "mode"])
    if mode_col is None:
        logger.warning("[%s] Mode column not found — no filter applied", sheet_name)
        return df.copy()
    return df[df[mode_col].astype(str).str.strip().str.upper() == LU_MODE_CODE].copy()


def _filter_by_asc(df: pd.DataFrame, sheet_name: str) -> pd.DataFrame:
    """
    Keep rows whose ASC code ends with 'u' (convention for LU stations).
    Station_Entries / Station_Exits don't have a Mode column, so we rely on
    the ASC suffix convention documented in NUMBAT.
    """
    asc_col = _find_col(df, ["ASC", "asc"])
    if asc_col is None:
        logger.warning("[%s] ASC column not found — returning all rows", sheet_name)
        return df.copy()
    mask = df[asc_col].astype(str).str.strip().str.endswith(LU_ASC_SUFFIX)
    return df[mask].copy()


def _filter_by_line(df: pd.DataFrame, sheet_name: str) -> pd.DataFrame:
    """
    Keep link rows whose Link identifier contains a known LU line code.
    The Link column format is: FROM_ASC_LINECD_DIR>TO_ASC_LINECD_DIR@LINECD
    """
    # Try Line column first
    line_col = _find_col(df, ["Line", "line"])
    if line_col is not None:
        # Line name column (e.g. 'Bakerloo', 'Central')
        lu_names = {
            "Bakerloo", "Central", "District", "H&C and Circle",
            "Jubilee", "Metropolitan", "Northern", "Piccadilly",
            "Victoria", "Waterloo & City",
        }
        mask = df[line_col].astype(str).str.strip().isin(lu_names)
        result = df[mask].copy()
        if len(result) > 0:
            return result

    # Fall back to parsing the Link column
    link_col = _find_col(df, ["Link", "link"])
    if link_col is None:
        logger.warning("[%s] Neither Line nor Link column found", sheet_name)
        return df.copy()

    def _is_lu_link(val: str) -> bool:
        # e.g. ELEu_BAK_NB>LAMu_BAK_NB@BAK → extract BAK
        try:
            code = val.split("@")[-1].split("_")[0].upper()
            return code in LU_LINE_CODES
        except Exception:
            return False

    mask = df[link_col].astype(str).apply(_is_lu_link)
    return df[mask].copy()


def _filter_flows(df: pd.DataFrame, sheet_name: str) -> pd.DataFrame:
    """
    Station_Flows: keep records where From or To ASC ends with 'u'.
    Many flows are within complex interchange stations; we keep any flow
    that involves at least one LU station node.
    """
    from_asc = _find_col(df, ["From ASC", "from_asc"])
    to_asc   = _find_col(df, ["To ASC",   "to_asc"])

    if from_asc is None and to_asc is None:
        logger.warning("[%s] No ASC columns found — returning all rows", sheet_name)
        return df.copy()

    mask = pd.Series(False, index=df.index)
    if from_asc:
        mask |= df[from_asc].astype(str).str.strip().str.endswith(LU_ASC_SUFFIX)
    if to_asc:
        mask |= df[to_asc].astype(str).str.strip().str.endswith(LU_ASC_SUFFIX)

    return df[mask].copy()


def _find_col(df: pd.DataFrame, candidates: list[str]) -> Optional[str]:
    """Find the first matching column name (case-insensitive) from candidates."""
    lower_map = {c.lower().strip(): c for c in df.columns}
    for c in candidates:
        matched = lower_map.get(c.lower().strip())
        if matched is not None:
            return matched
    return None

