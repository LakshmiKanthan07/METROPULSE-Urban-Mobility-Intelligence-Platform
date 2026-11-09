"""
METROPULSE — Temporal Analysis
Analyses demand patterns across years, day types, and time-of-day.
"""
import logging

import pandas as pd
import numpy as np

from src.config.settings import DATA_CSV
from src.pipeline.run_pipeline import load_dataset

logger = logging.getLogger(__name__)


def run_temporal_analysis() -> dict[str, pd.DataFrame]:
    """
    Produce year-on-year and weekday/weekend temporal analyses.
    """
    results = {}

    # ── 1. Year-on-Year boarder comparison ──────────────────────────────────
    try:
        boarders = load_dataset("tube_line_boarders")
        yoy = (
            boarders
            .groupby(["line_code", "line_name", "year", "day_type"])["total"]
            .max()
            .reset_index()
            .rename(columns={"total": "daily_boarders"})
        )
        # Pivot for easy comparison
        yoy_pivot = yoy.pivot_table(
            index=["line_code", "line_name", "day_type"],
            columns="year",
            values="daily_boarders",
        ).reset_index()
        results["yoy_line_boarders"] = yoy_pivot
        yoy_pivot.to_csv(DATA_CSV / "temporal_yoy_line_boarders.csv", index=False)
        logger.info("YoY line boarders: %d records", len(yoy_pivot))
    except Exception as exc:
        logger.error("YoY boarders failed: %s", exc)

    # ── 2. Weekday vs Weekend profile ───────────────────────────────────────
    try:
        entries = load_dataset("tube_station_entries")
        entries["is_weekend"] = entries["day_type"].isin(["SAT", "SUN"])
        wk = (
            entries
            .groupby(["start_minute", "time_interval", "period",
                      "is_weekend", "year"])["passengers"]
            .sum()
            .reset_index()
        )
        results["weekday_weekend_profile"] = wk
        wk.to_csv(DATA_CSV / "temporal_weekday_weekend.csv", index=False)
    except Exception as exc:
        logger.error("Weekday/Weekend profile failed: %s", exc)

    # ── 3. Friday vs Monday vs TWT ──────────────────────────────────────────
    try:
        boarders = load_dataset("tube_line_boarders")
        day_cmp = (
            boarders
            .groupby(["day_type", "day_type_label", "year"])["total"]
            .sum()
            .reset_index()
        )
        results["day_type_comparison"] = day_cmp
        day_cmp.to_csv(DATA_CSV / "temporal_day_type_comparison.csv", index=False)
    except Exception as exc:
        logger.error("Day type comparison failed: %s", exc)

    # ── 4. Station inflow/outflow asymmetry ─────────────────────────────────
    try:
        entries = load_dataset("tube_station_entries")
        exits   = load_dataset("tube_station_exits")

        ent_agg = (
            entries.groupby(["nlc", "asc", "station", "year", "day_type"])["total"]
            .max().reset_index().rename(columns={"total": "entries"})
        )
        ext_agg = (
            exits.groupby(["nlc", "asc", "station", "year", "day_type"])["total"]
            .max().reset_index().rename(columns={"total": "exits"})
        )
        flow = ent_agg.merge(
            ext_agg[["nlc", "year", "day_type", "exits"]],
            on=["nlc", "year", "day_type"], how="outer"
        )
        flow["net_flow"] = flow["entries"].fillna(0) - flow["exits"].fillna(0)
        flow["inflow_ratio"] = flow["entries"] / (flow["exits"].replace(0, np.nan))
        results["station_flow_asymmetry"] = flow
        flow.to_csv(DATA_CSV / "temporal_station_flow_asymmetry.csv", index=False)
        logger.info("Station flow asymmetry: %d records", len(flow))
    except Exception as exc:
        logger.error("Station flow asymmetry failed: %s", exc)

    return results

