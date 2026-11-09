"""
METROPULSE — Workbook Reader
Discovers and reads TfL NUMBAT Excel workbooks from data/raw/.
"""
import logging
import re
from pathlib import Path
from typing import Optional

import pandas as pd

from src.config.settings import DATA_RAW, WORKSHEETS, DAY_TYPE_MAP

logger = logging.getLogger(__name__)

# ─── Filename pattern: NBTyyDDD_outputs.xlsx or NBTyyDDD_Outputs.xlsx
_FILE_PATTERN = re.compile(
    r"NBT(\d{2})(MON|TWT|FRI|SAT|SUN)_[Oo]utputs\.xlsx$",
    re.IGNORECASE,
)


def discover_files(raw_dir: Path = DATA_RAW) -> list[dict]:
    """
    Discover all NUMBAT workbooks in raw_dir.

    Returns a list of dicts with keys:
        path, filename, year, day_type_code, day_type_label
    """
    found = []
    for f in sorted(raw_dir.glob("NBT*.xlsx")):
        m = _FILE_PATTERN.match(f.name)
        if not m:
            logger.warning("Skipping unrecognised file: %s", f.name)
            continue
        yr_suffix, day_code = m.group(1), m.group(2).upper()
        year = int("20" + yr_suffix)
        found.append(
            {
                "path":           f,
                "filename":       f.name,
                "year":           year,
                "day_type_code":  day_code,
                "day_type_label": DAY_TYPE_MAP.get(day_code, day_code),
                "file_size_mb":   round(f.stat().st_size / 1_048_576, 2),
            }
        )
    logger.info("Discovered %d workbooks in %s", len(found), raw_dir)
    return found


def list_sheets(path: Path) -> list[str]:
    """Return sheet names for the given workbook (without loading data)."""
    xl = pd.ExcelFile(path, engine="openpyxl")
    return xl.sheet_names


def read_sheet(
    path: Path,
    sheet_name: str,
    header_row: int = 2,
    *,
    year: Optional[int] = None,
    day_type_code: Optional[str] = None,
    source_file: Optional[str] = None,
) -> Optional[pd.DataFrame]:
    """
    Read a single worksheet from a workbook.

    Parameters
    ----------
    path : Path
        Workbook path.
    sheet_name : str
        Target worksheet name.
    header_row : int
        0-indexed row to use as column header (default 2 → 3rd row).
    year, day_type_code, source_file : optional
        Metadata columns injected into the returned DataFrame.

    Returns
    -------
    DataFrame or None if sheet is missing.
    """
    try:
        df = pd.read_excel(
            path,
            sheet_name=sheet_name,
            header=header_row,
            engine="openpyxl",
        )
    except Exception as exc:
        logger.warning("Cannot read sheet '%s' from %s: %s", sheet_name, path.name, exc)
        return None

    # Drop entirely empty rows and columns
    df = df.dropna(how="all").dropna(axis=1, how="all")

    # Standardize column headers: string cast and strip whitespace
    df.columns = [str(c).strip() for c in df.columns]
    # Remove duplicate columns within sheet if any
    df = df.loc[:, ~df.columns.duplicated(keep="first")]

    # Inject metadata
    if year is not None:
        df["year"] = year
    if day_type_code is not None:
        df["day_type"] = day_type_code
    if source_file is not None:
        df["source_file"] = source_file

    return df


def read_all_sheets(
    file_info: dict,
    target_sheets: Optional[list[str]] = None,
) -> dict[str, pd.DataFrame]:
    """
    Read all (or selected) worksheets from a single workbook.

    Parameters
    ----------
    file_info : dict
        Entry produced by discover_files().
    target_sheets : list[str] or None
        Specific worksheets to read; if None, reads WORKSHEETS from settings.

    Returns
    -------
    Dict mapping sheet_name → DataFrame.
    """
    path       = file_info["path"]
    year       = file_info["year"]
    day_type   = file_info["day_type_code"]
    source_file = file_info["filename"]

    available = list_sheets(path)
    sheets_to_read = target_sheets or WORKSHEETS

    results: dict[str, pd.DataFrame] = {}
    for sheet in sheets_to_read:
        # Case-insensitive match against available sheets
        matched = next(
            (s for s in available if s.lower() == sheet.lower()), None
        )
        if matched is None:
            logger.debug("Sheet '%s' not found in %s", sheet, path.name)
            continue

        # Cover sheet doesn't have the same 2-row sub-header; read as-is
        hdr = 0 if sheet == "_Cover" else 2

        df = read_sheet(
            path, matched,
            header_row=hdr,
            year=year,
            day_type_code=day_type,
            source_file=source_file,
        )
        if df is not None and not df.empty:
            results[sheet] = df
            logger.debug(
                "  %-25s  %4d rows × %3d cols  (%s)",
                sheet, len(df), len(df.columns), path.name,
            )

    return results

