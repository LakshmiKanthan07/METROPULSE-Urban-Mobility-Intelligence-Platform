"""
METROPULSE — Comprehensive Data Quality Reports Generator
Generates:
  1. data_quality_summary.csv
  2. missing_values_report.csv
  3. duplicate_records_report.csv
  4. schema_comparison.csv
Writes to both reports/ and reports/data_quality/
"""
import logging
import sys
from pathlib import Path

# Ensure project root is in sys.path
_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import pandas as pd
import numpy as np
import openpyxl

from src.config.settings import DATA_CSV, DATA_PARQUET, REPORTS_DIR, DATA_RAW
from src.ingestion.workbook_reader import discover_files

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)-8s | %(message)s")
logger = logging.getLogger("quality_generator")

def get_sheet_names(path: Path) -> list[str]:
    wb = openpyxl.load_workbook(path, read_only=True, keep_links=False)
    names = wb.sheetnames
    wb.close()
    return names

def generate_quality_reports():
    out_dir_reports = REPORTS_DIR
    out_dir_dq = REPORTS_DIR / "data_quality"
    out_dir_reports.mkdir(parents=True, exist_ok=True)
    out_dir_dq.mkdir(parents=True, exist_ok=True)

    dataset_names = [
        "tube_link_loads",
        "tube_link_frequencies",
        "tube_line_boarders",
        "tube_station_entries",
        "tube_station_exits",
        "tube_station_boarders",
        "tube_station_alighters",
        "tube_station_flows",
    ]

    summary_rows = []
    missing_rows = []
    duplicate_rows = []

    # Composite key definitions by dataset
    COMPOSITE_KEYS = {
        "tube_link_loads":        ["link", "direction", "time_interval", "year", "day_type"],
        "tube_link_frequencies":  ["link", "direction", "time_interval", "year", "day_type"],
        "tube_line_boarders":     ["line_code", "time_interval", "year", "day_type"],
        "tube_station_entries":   ["asc", "time_interval", "year", "day_type"],
        "tube_station_exits":     ["asc", "time_interval", "year", "day_type"],
        "tube_station_boarders":  ["asc", "line", "direction", "platform", "time_interval", "year", "day_type"],
        "tube_station_alighters": ["asc", "line", "direction", "platform", "time_interval", "year", "day_type"],
        "tube_station_flows":     ["complex_nlc", "from_asc", "from_node", "to_asc", "to_node", "movement", "time_interval", "year", "day_type"],
    }

    logger.info("Scanning processed Parquet/CSV datasets...")
    for name in dataset_names:
        pq_path = DATA_PARQUET / f"{name}.parquet"
        csv_path = DATA_CSV / f"{name}.csv"

        if pq_path.exists():
            df = pd.read_parquet(pq_path)
        elif csv_path.exists():
            df = pd.read_csv(csv_path)
        else:
            logger.warning("Dataset %s not found", name)
            continue

        total_rows = len(df)
        total_cols = len(df.columns)

        # Missing values
        null_counts = df.isnull().sum()
        total_nulls = int(null_counts.sum())

        for col, cnt in null_counts.items():
            if cnt > 0:
                missing_rows.append({
                    "dataset": name,
                    "column": col,
                    "missing_count": int(cnt),
                    "total_rows": total_rows,
                    "pct_missing": round(float(cnt) / total_rows * 100, 3)
                })

        # Duplicates using specific composite keys
        target_keys = COMPOSITE_KEYS.get(name, [])
        key_cols = [c for c in target_keys if c in df.columns]
        if key_cols:
            dupes = int(df.duplicated(subset=key_cols).sum())
        else:
            dupes = int(df.duplicated().sum())

        duplicate_rows.append({
            "dataset": name,
            "key_columns_checked": "; ".join(key_cols) if key_cols else "ALL_COLUMNS",
            "duplicate_count": dupes,
            "total_rows": total_rows,
            "pct_duplicate": round(float(dupes) / total_rows * 100, 4)
        })

        # Negative values check
        num_cols = df.select_dtypes(include=[np.number]).columns
        neg_count = 0
        for nc in num_cols:
            neg_count += int((df[nc] < 0).sum())

        summary_rows.append({
            "dataset": name,
            "total_rows": total_rows,
            "total_columns": total_cols,
            "total_missing_values": total_nulls,
            "duplicate_records": dupes,
            "negative_values": neg_count,
            "status": "PASS" if dupes == 0 and neg_count == 0 else "FLAGGED"
        })

    # If missing_rows is empty, add a clean entry
    if not missing_rows:
        missing_rows.append({
            "dataset": "ALL_DATASETS",
            "column": "NONE",
            "missing_count": 0,
            "total_rows": sum(r["total_rows"] for r in summary_rows),
            "pct_missing": 0.0
        })

    df_summary = pd.DataFrame(summary_rows)
    df_missing = pd.DataFrame(missing_rows)
    df_duplicates = pd.DataFrame(duplicate_rows)

    # 4. Schema Comparison Across Years
    logger.info("Computing cross-year schema comparison...")
    files = discover_files()
    schema_rows = []

    # Map sheets to check across years
    sheets_to_check = [
        "Link_Loads", "Link_Frequencies", "Line_Boarders",
        "Station_Entries", "Station_Exits", "Station_Boarders",
        "Station_Alighters", "Station_Flows"
    ]

    for sheet in sheets_to_check:
        cols_by_year = {}
        for fi in files:
            yr = fi["year"]
            if yr not in cols_by_year:
                all_sheets = get_sheet_names(fi["path"])
                matched = [s for s in all_sheets if s.lower() == sheet.lower()]
                if matched:
                    # Read only 1 row to get columns quickly
                    sample_df = pd.read_excel(fi["path"], sheet_name=matched[0], nrows=1)
                    cols_by_year[yr] = [str(c).strip() for c in sample_df.columns]

        years = sorted(cols_by_year.keys())
        cols_2023 = cols_by_year.get(2023, [])
        cols_2024 = cols_by_year.get(2024, [])
        cols_2025 = cols_by_year.get(2025, [])

        common_cols = set(cols_2023) & set(cols_2024) & set(cols_2025)
        all_cols = set(cols_2023) | set(cols_2024) | set(cols_2025)
        diff_cols = all_cols - common_cols

        schema_rows.append({
            "sheet_name": sheet,
            "columns_2023_count": len(cols_2023),
            "columns_2024_count": len(cols_2024),
            "columns_2025_count": len(cols_2025),
            "common_columns_count": len(common_cols),
            "schema_consistent": len(diff_cols) == 0,
            "divergent_columns": "; ".join(sorted(diff_cols)) if diff_cols else "None (100% Identical)",
            "standardization_action": "Standardized to canonical schema in ETL Stage 2"
        })

    df_schema = pd.DataFrame(schema_rows)

    # Save to both reports/ and reports/data_quality/
    for folder in [out_dir_reports, out_dir_dq]:
        df_summary.to_csv(folder / "data_quality_summary.csv", index=False)
        df_missing.to_csv(folder / "missing_values_report.csv", index=False)
        df_duplicates.to_csv(folder / "duplicate_records_report.csv", index=False)
        df_schema.to_csv(folder / "schema_comparison.csv", index=False)

    logger.info("Quality CSV reports successfully written to %s and %s", out_dir_reports, out_dir_dq)

if __name__ == "__main__":
    generate_quality_reports()
