"""
METROPULSE — Data Validation
Validates cleaned datasets and produces quality reports.
"""
import logging
from pathlib import Path
from typing import Optional

import pandas as pd
import numpy as np

from src.config.settings import REPORTS_DIR, LU_LINE_CODES

logger = logging.getLogger(__name__)


# ─── Thresholds ───────────────────────────────────────────────────────────────
MAX_DAILY_PASSENGERS_LINK    = 300_000  # sanity upper bound per link per day
MAX_DAILY_PASSENGERS_STATION = 1_000_000  # sanity upper bound per station per day
MIN_PASSENGERS               = 0.0


def validate_dataset(
    df: pd.DataFrame,
    name: str,
    *,
    passenger_col: str = "total",
    expected_line_codes: Optional[set] = None,
) -> dict:
    """
    Run validation checks on a cleaned dataset.

    Returns a dict with counts for each check.
    """
    results = {"dataset": name, "total_rows": len(df)}

    # 1. Missing values
    missing = df.isnull().sum()
    results["missing_total"] = int(missing.sum())
    results["missing_by_col"] = missing[missing > 0].to_dict()

    # 2. Duplicates
    key_cols = [c for c in ["link", "nlc", "asc", "line_code", "id",
                              "time_interval", "year", "day_type"]
                if c in df.columns]
    if key_cols:
        dupes = df.duplicated(subset=key_cols).sum()
        results["duplicate_rows"] = int(dupes)
    else:
        results["duplicate_rows"] = 0

    # 3. Negative passenger counts
    if passenger_col in df.columns:
        neg = (df[passenger_col] < MIN_PASSENGERS).sum()
        results["negative_passengers"] = int(neg)

        # 4. Implausibly high passenger counts
        threshold = MAX_DAILY_PASSENGERS_LINK
        high = (df[passenger_col] > threshold).sum()
        results["implausibly_high_passengers"] = int(high)
    else:
        results["negative_passengers"] = None
        results["implausibly_high_passengers"] = None

    # 5. Invalid line codes (if applicable)
    if "line_code" in df.columns and expected_line_codes:
        inv = (~df["line_code"].isin(expected_line_codes)).sum()
        results["invalid_line_codes"] = int(inv)
    else:
        results["invalid_line_codes"] = None

    # 6. Missing station identifiers
    for id_col in ["nlc", "asc", "from_asc", "to_asc"]:
        if id_col in df.columns:
            miss = df[id_col].isnull().sum()
            results[f"missing_{id_col}"] = int(miss)

    # 7. Invalid time intervals (if present)
    if "time_interval" in df.columns:
        import re
        pattern = re.compile(r"^\d{4}-\d{4}$")
        invalid_ti = df["time_interval"].astype(str).apply(
            lambda x: not pattern.match(x)
        ).sum()
        results["invalid_time_intervals"] = int(invalid_ti)

    # 8. Summary flag
    critical = results.get("negative_passengers", 0) or 0
    critical += results.get("duplicate_rows", 0) or 0
    results["has_critical_issues"] = critical > 0

    return results


def build_quality_report(validations: list[dict]) -> pd.DataFrame:
    """Convert list of validation dicts to a summary DataFrame."""
    return pd.DataFrame(validations)


def save_quality_reports(
    validations: list[dict],
    missing_df: Optional[pd.DataFrame] = None,
    dupe_df: Optional[pd.DataFrame] = None,
) -> None:
    """Write quality CSVs to reports/data_quality/."""
    out_dir = REPORTS_DIR / "data_quality"
    out_dir.mkdir(parents=True, exist_ok=True)

    summary = build_quality_report(validations)
    summary.to_csv(out_dir / "data_quality_summary.csv", index=False)

    if missing_df is not None:
        missing_df.to_csv(out_dir / "missing_values_report.csv", index=False)

    if dupe_df is not None:
        dupe_df.to_csv(out_dir / "duplicate_records_report.csv", index=False)

    logger.info("Quality reports saved to %s", out_dir)

