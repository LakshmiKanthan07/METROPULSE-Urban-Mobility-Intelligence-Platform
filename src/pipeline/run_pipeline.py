"""
METROPULSE — Full ETL Pipeline
Orchestrates extraction, transformation, LU filtering, validation and loading
for all 15 NUMBAT workbooks.
"""
import logging
import sys
from pathlib import Path

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

# Ensure project root is on path when run directly
_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from src.config.settings import (
    DATA_CSV, DATA_PARQUET, DATA_RAW,
    LU_LINE_CODES, LOGS_DIR,
)
from src.ingestion.workbook_reader import discover_files, read_all_sheets
from src.preprocessing.mode_filter import filter_lu
from src.preprocessing.standardization import (
    standardise_link_loads,
    standardise_line_boarders,
    standardise_station_entries_exits,
    standardise_station_boarders_alighters,
    standardise_station_flows,
)
from src.preprocessing.cleaning import (
    clean_common, normalise_direction, add_day_type_label,
    add_period_label, add_start_minute,
)
from src.preprocessing.validation import validate_dataset, save_quality_reports
from src.ingestion.inventory import build_inventory, save_inventory, print_summary

logger = logging.getLogger(__name__)

# ─── Mapping: sheet → standardise function + filtered flag ───────────────────
SHEET_HANDLERS = {
    "Link_Loads":          (standardise_link_loads,                  False),
    "Link_Frequencies":    (standardise_link_loads,                  False),  # same schema
    "Line_Boarders":       (standardise_line_boarders,               True),   # has Mode col
    "Station_Entries":     (standardise_station_entries_exits,       False),
    "Station_Exits":       (standardise_station_entries_exits,       False),
    "Station_Boarders":    (standardise_station_boarders_alighters,  True),
    "Station_Alighters":   (standardise_station_boarders_alighters,  True),
    "Station_Flows":       (standardise_station_flows,               False),
}

# Output dataset names
DATASET_NAMES = {
    "Link_Loads":        "tube_link_loads",
    "Link_Frequencies":  "tube_link_frequencies",
    "Line_Boarders":     "tube_line_boarders",
    "Station_Entries":   "tube_station_entries",
    "Station_Exits":     "tube_station_exits",
    "Station_Boarders":  "tube_station_boarders",
    "Station_Alighters": "tube_station_alighters",
    "Station_Flows":     "tube_station_flows",
}


def run_inventory() -> pd.DataFrame:
    """Stage 0: Build source data inventory."""
    logger.info("=" * 60)
    logger.info("STAGE 0 — SOURCE DATA INVENTORY")
    logger.info("=" * 60)
    inventory = build_inventory()
    save_inventory(inventory)
    print_summary(inventory)
    return inventory


def run_pipeline() -> dict[str, pd.DataFrame]:
    """
    Main ETL pipeline.

    Returns dict of dataset_name → clean DataFrame.
    """
    logger.info("=" * 60)
    logger.info("STAGE 1 — EXTRACT")
    logger.info("=" * 60)

    files = discover_files()
    if not files:
        raise FileNotFoundError(f"No NUMBAT workbooks found in {DATA_RAW}")

    # Accumulate raw DataFrames per sheet
    raw_buffers: dict[str, list[pd.DataFrame]] = {s: [] for s in SHEET_HANDLERS}

    for fi in files:
        logger.info("Processing %s (year=%d, day_type=%s)",
                    fi["filename"], fi["year"], fi["day_type_code"])
        sheets_data = read_all_sheets(fi, target_sheets=list(SHEET_HANDLERS.keys()))
        for sheet, df in sheets_data.items():
            if sheet in raw_buffers:
                raw_buffers[sheet].append(df)

    logger.info("=" * 60)
    logger.info("STAGE 2 — TRANSFORM & FILTER")
    logger.info("=" * 60)

    validations: list[dict] = []
    datasets: dict[str, pd.DataFrame] = {}

    for sheet, dfs in raw_buffers.items():
        if not dfs:
            logger.warning("No data collected for sheet '%s'", sheet)
            continue

        handler_fn, is_mode_filtered = SHEET_HANDLERS[sheet]
        logger.info("Processing sheet: %s (%d files)", sheet, len(dfs))

        # Concatenate all years/day-types
        raw_all = pd.concat(dfs, ignore_index=True)

        # Apply LU filter
        filtered = filter_lu(raw_all, sheet)

        # Standardise schema
        try:
            std = handler_fn(filtered)
        except Exception as exc:
            logger.error("Standardisation failed for %s: %s", sheet, exc)
            continue

        # Clean
        std = clean_common(std)
        std = normalise_direction(std)
        std = add_day_type_label(std)
        std = add_period_label(std)
        std = add_start_minute(std)

        dataset_name = DATASET_NAMES[sheet]
        datasets[dataset_name] = std

        # Validate
        v = validate_dataset(
            std, dataset_name,
            passenger_col="passengers" if "passengers" in std.columns else "total",
            expected_line_codes=LU_LINE_CODES,
        )
        validations.append(v)
        logger.info(
            "  %-30s  %7d rows | missing=%d | dupes=%d | neg_pax=%s",
            dataset_name, v["total_rows"],
            v["missing_total"], v["duplicate_rows"],
            v.get("negative_passengers"),
        )

    logger.info("=" * 60)
    logger.info("STAGE 3 — LOAD")
    logger.info("=" * 60)

    for name, df in datasets.items():
        _save_csv(df, name)
        _save_parquet(df, name)

    save_quality_reports(validations)

    logger.info("Pipeline complete. Datasets saved:")
    for name, df in datasets.items():
        logger.info("  %-35s  %7d rows", name, len(df))

    return datasets


def _save_csv(df: pd.DataFrame, name: str) -> Path:
    DATA_CSV.mkdir(parents=True, exist_ok=True)
    path = DATA_CSV / f"{name}.csv"
    df.to_csv(path, index=False)
    logger.info("  CSV → %s", path)
    return path


def _save_parquet(df: pd.DataFrame, name: str) -> Path:
    DATA_PARQUET.mkdir(parents=True, exist_ok=True)
    path = DATA_PARQUET / f"{name}.parquet"
    df.to_parquet(path, index=False, engine="pyarrow")
    logger.info("  Parquet → %s", path)
    return path


def load_dataset(name: str) -> pd.DataFrame:
    """
    Load a processed dataset from Parquet (fast) or CSV fallback.
    """
    parquet_path = DATA_PARQUET / f"{name}.parquet"
    csv_path     = DATA_CSV / f"{name}.csv"

    if parquet_path.exists():
        return pd.read_parquet(parquet_path, engine="pyarrow")
    elif csv_path.exists():
        return pd.read_csv(csv_path)
    else:
        raise FileNotFoundError(
            f"Dataset '{name}' not found. Run the pipeline first."
        )

