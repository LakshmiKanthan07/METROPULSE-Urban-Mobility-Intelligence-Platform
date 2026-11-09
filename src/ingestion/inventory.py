"""
METROPULSE — Source Data Inventory
Generates a comprehensive inventory of all raw NUMBAT workbooks.
"""
import logging
from pathlib import Path

import pandas as pd

from src.config.settings import DATA_RAW, REPORTS_DIR, WORKSHEETS
from src.ingestion.workbook_reader import discover_files, list_sheets, read_sheet

logger = logging.getLogger(__name__)


def build_inventory(raw_dir: Path = DATA_RAW) -> pd.DataFrame:
    """
    Build a row-per-worksheet inventory for all discovered workbooks.

    Returns a DataFrame with columns:
        filename, year, day_type_code, day_type_label, file_size_mb,
        sheet_name, row_count, col_count, columns, missing_pct
    """
    files = discover_files(raw_dir)
    records = []

    for fi in files:
        available_sheets = list_sheets(fi["path"])
        for sheet in WORKSHEETS:
            matched = next(
                (s for s in available_sheets if s.lower() == sheet.lower()), None
            )
            if matched is None:
                records.append(
                    {
                        **fi,
                        "sheet_name":  sheet,
                        "present":     False,
                        "row_count":   None,
                        "col_count":   None,
                        "columns":     None,
                        "missing_pct": None,
                    }
                )
                continue

            hdr = 0 if sheet == "_Cover" else 2
            try:
                df = read_sheet(fi["path"], matched, header_row=hdr)
            except Exception as exc:
                logger.warning("Error reading %s / %s: %s", fi["filename"], sheet, exc)
                records.append(
                    {
                        **fi,
                        "sheet_name":  sheet,
                        "present":     True,
                        "row_count":   -1,
                        "col_count":   -1,
                        "columns":     str(exc),
                        "missing_pct": None,
                    }
                )
                continue

            if df is None or df.empty:
                records.append(
                    {
                        **fi,
                        "sheet_name":  sheet,
                        "present":     True,
                        "row_count":   0,
                        "col_count":   0,
                        "columns":     "",
                        "missing_pct": 0.0,
                    }
                )
                continue

            # Drop metadata cols injected by read_sheet
            data_cols = [c for c in df.columns if c not in ("year", "day_type", "source_file")]
            missing_pct = round(
                df[data_cols].isnull().sum().sum()
                / max(df[data_cols].size, 1)
                * 100,
                2,
            )

            records.append(
                {
                    **fi,
                    "sheet_name":  sheet,
                    "present":     True,
                    "row_count":   len(df),
                    "col_count":   len(data_cols),
                    "columns":     "|".join(str(c) for c in data_cols[:20]),
                    "missing_pct": missing_pct,
                }
            )
            logger.info(
                "  %-40s  %-20s  %4d rows  %.1f%% missing",
                fi["filename"], sheet, len(df), missing_pct,
            )

    inventory = pd.DataFrame(records)
    # Drop internal Path object
    inventory["path"] = inventory["path"].astype(str)
    return inventory


def save_inventory(inventory: pd.DataFrame) -> Path:
    """Save inventory to reports/data_quality/ and return path."""
    out_path = REPORTS_DIR / "data_quality" / "source_inventory.csv"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    inventory.to_csv(out_path, index=False)
    logger.info("Inventory saved → %s", out_path)
    return out_path


def print_summary(inventory: pd.DataFrame) -> None:
    """Print a human-readable summary."""
    files_found = inventory["filename"].nunique()
    sheets_present = inventory[inventory["present"] == True]
    total_rows = sheets_present["row_count"].dropna().sum()
    print(f"\n{'='*60}")
    print(f"  METROPULSE — Source Data Inventory")
    print(f"{'='*60}")
    print(f"  Workbooks discovered : {files_found}")
    print(f"  Years covered        : {sorted(inventory['year'].unique())}")
    print(f"  Day types            : {sorted(inventory['day_type_code'].unique())}")
    print(f"  Worksheets expected  : {inventory['sheet_name'].nunique()}")
    sheets_always_present = (
        inventory.groupby("sheet_name")["present"].all()
    )
    print(f"  Sheets in all files  : {sheets_always_present.sum()}")
    print(f"  Total data rows read : {int(total_rows):,}")
    print(f"{'='*60}\n")
    pivot = inventory.pivot_table(
        index="sheet_name",
        values="present",
        aggfunc="sum",
        fill_value=0,
    )
    print(pivot.to_string())
    print()

