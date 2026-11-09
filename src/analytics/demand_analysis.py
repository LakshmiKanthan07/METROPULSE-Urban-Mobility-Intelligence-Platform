"""
METROPULSE — Demand Analysis
Core passenger demand analytics and BI export generation.
"""
import logging
from pathlib import Path

import numpy as np
import pandas as pd

from src.config.settings import DATA_CSV, DATA_PARQUET, DATA_BI, REPORTS_DIR
from src.pipeline.run_pipeline import load_dataset

logger = logging.getLogger(__name__)


def run_demand_analysis() -> dict[str, pd.DataFrame]:
    """
    Compute station demand rankings, line rankings, boarder profiles etc.
    Returns dict of result DataFrames.
    """
    results = {}

    # ── 1. Station demand rankings ──────────────────────────────────────────
    try:
        entries = load_dataset("tube_station_entries")
        # Daily total by station, year, day_type
        daily = (
            entries
            .groupby(["nlc", "asc", "station", "year", "day_type"], dropna=False)["total"]
            .max()  # total col is already the daily total
            .reset_index()
            .rename(columns={"total": "daily_entries"})
        )
        results["station_demand"] = daily
        logger.info("Station demand: %d records", len(daily))
    except Exception as exc:
        logger.error("Station demand failed: %s", exc)

    # ── 2. Line demand rankings ──────────────────────────────────────────────
    try:
        boarders = load_dataset("tube_line_boarders")
        line_daily = (
            boarders
            .groupby(["line_code", "line_name", "year", "day_type"])["total"]
            .max()
            .reset_index()
            .rename(columns={"total": "daily_boarders"})
        )
        results["line_demand"] = line_daily
        logger.info("Line demand: %d records", len(line_daily))
    except Exception as exc:
        logger.error("Line demand failed: %s", exc)

    # ── 3. Time-of-day profiles ─────────────────────────────────────────────
    try:
        entries = load_dataset("tube_station_entries")
        time_profile = (
            entries[entries["time_interval"].notna()]
            .groupby(["time_interval", "start_minute", "period", "year", "day_type"])["passengers"]
            .sum()
            .reset_index()
        )
        results["time_profile"] = time_profile
    except Exception as exc:
        logger.error("Time profile failed: %s", exc)

    # ── 4. Weekday vs Weekend ───────────────────────────────────────────────
    try:
        boarders = load_dataset("tube_line_boarders")
        boarders["is_weekend"] = boarders["day_type"].isin(["SAT", "SUN"])
        wk_comparison = (
            boarders
            .groupby(["line_code", "line_name", "year", "is_weekend"])["total"]
            .mean()
            .reset_index()
            .rename(columns={"total": "avg_daily_boarders"})
        )
        results["weekday_weekend"] = wk_comparison
    except Exception as exc:
        logger.error("Weekday/Weekend comparison failed: %s", exc)

    # ── 5. Station exits ────────────────────────────────────────────────────
    try:
        exits = load_dataset("tube_station_exits")
        exit_daily = (
            exits
            .groupby(["nlc", "asc", "station", "year", "day_type"])["total"]
            .max()
            .reset_index()
            .rename(columns={"total": "daily_exits"})
        )
        results["station_exits"] = exit_daily
    except Exception as exc:
        logger.error("Station exits failed: %s", exc)

    # Save all results
    _save_results(results, prefix="demand")
    return results


def generate_bi_exports() -> None:
    """Generate star-schema BI-ready CSV exports."""
    DATA_BI.mkdir(parents=True, exist_ok=True)
    logger.info("Generating BI exports...")

    # ── fact_station_demand ──────────────────────────────────────────────────
    try:
        entries = load_dataset("tube_station_entries")
        exits   = load_dataset("tube_station_exits")

        ent = (
            entries
            .groupby(["nlc", "asc", "station", "fare_zone", "year", "day_type",
                      "day_type_label"])["total"]
            .max()
            .reset_index()
            .rename(columns={"total": "daily_entries"})
        )
        ext = (
            exits
            .groupby(["nlc", "asc", "station", "year", "day_type"])["total"]
            .max()
            .reset_index()
            .rename(columns={"total": "daily_exits"})
        )
        fact_station = ent.merge(
            ext[["nlc", "year", "day_type", "daily_exits"]],
            on=["nlc", "year", "day_type"], how="left"
        )
        fact_station.to_csv(DATA_BI / "fact_station_demand.csv", index=False)
        logger.info("  fact_station_demand: %d rows", len(fact_station))
    except Exception as exc:
        logger.error("fact_station_demand failed: %s", exc)

    # ── fact_link_demand ─────────────────────────────────────────────────────
    try:
        links = load_dataset("tube_link_loads")
        fact_link = (
            links
            .groupby(["link", "line", "line_code", "direction",
                      "from_station", "to_station", "year", "day_type"])
            [["total", "early", "am_peak", "midday", "pm_peak", "evening", "late"]]
            .max()
            .reset_index()
        )
        fact_link.to_csv(DATA_BI / "fact_link_demand.csv", index=False)
        logger.info("  fact_link_demand: %d rows", len(fact_link))
    except Exception as exc:
        logger.error("fact_link_demand failed: %s", exc)

    # ── fact_service_frequency ───────────────────────────────────────────────
    try:
        freqs = load_dataset("tube_link_frequencies")
        fact_freq = (
            freqs
            .groupby(["link", "line", "line_code", "direction",
                      "from_station", "to_station", "year", "day_type"])
            [["total", "am_peak", "pm_peak", "midday"]]
            .max()
            .reset_index()
        )
        fact_freq.to_csv(DATA_BI / "fact_service_frequency.csv", index=False)
        logger.info("  fact_service_frequency: %d rows", len(fact_freq))
    except Exception as exc:
        logger.error("fact_service_frequency failed: %s", exc)

    # ── dim_station ──────────────────────────────────────────────────────────
    try:
        entries = load_dataset("tube_station_entries")
        dim_station = (
            entries[["nlc", "asc", "station", "fare_zone"]]
            .drop_duplicates(subset=["nlc"])
            .sort_values("station")
            .reset_index(drop=True)
        )
        dim_station.to_csv(DATA_BI / "dim_station.csv", index=False)
        logger.info("  dim_station: %d stations", len(dim_station))
    except Exception as exc:
        logger.error("dim_station failed: %s", exc)

    # ── dim_line ─────────────────────────────────────────────────────────────
    try:
        boarders = load_dataset("tube_line_boarders")
        dim_line = (
            boarders[["line_code", "line_name"]]
            .drop_duplicates()
            .sort_values("line_name")
            .reset_index(drop=True)
        )
        dim_line.to_csv(DATA_BI / "dim_line.csv", index=False)
        logger.info("  dim_line: %d lines", len(dim_line))
    except Exception as exc:
        logger.error("dim_line failed: %s", exc)

    # ── dim_date_profile ─────────────────────────────────────────────────────
    from src.config.settings import DAY_TYPE_MAP
    dim_date = pd.DataFrame([
        {"year": y, "day_type": dt, "day_type_label": lbl,
         "is_weekend": dt in ("SAT", "SUN")}
        for y in [2023, 2024, 2025]
        for dt, lbl in DAY_TYPE_MAP.items()
    ])
    dim_date.to_csv(DATA_BI / "dim_date_profile.csv", index=False)

    # ── dim_time_interval ────────────────────────────────────────────────────
    intervals = []
    for h in range(5, 29):
        for q in range(4):
            actual_h = h % 24
            m = q * 15
            start = f"{actual_h:02d}{m:02d}"
            end_m = m + 15
            end_h = actual_h + (end_m // 60)
            end = f"{end_h % 24:02d}{end_m % 60:02d}"
            label = f"{start}-{end}"
            if h >= 29:
                break
            # Period label
            start_min = actual_h * 60 + m
            if start_min < 390:   period = "Early"
            elif start_min < 570: period = "AM Peak"
            elif start_min < 960: period = "Midday"
            elif start_min < 1140:period = "PM Peak"
            elif start_min < 1320:period = "Evening"
            else:                  period = "Late"
            intervals.append({"time_interval": label,
                               "start_minute": start_min,
                               "period": period})

    dim_time = pd.DataFrame(intervals)
    dim_time.to_csv(DATA_BI / "dim_time_interval.csv", index=False)
    logger.info("BI exports complete → %s", DATA_BI)


def _save_results(results: dict, prefix: str) -> None:
    """Save analytics results to processed/csv."""
    DATA_CSV.mkdir(parents=True, exist_ok=True)
    for name, df in results.items():
        path = DATA_CSV / f"{prefix}_{name}.csv"
        df.to_csv(path, index=False)
        logger.info("  Saved → %s", path)

