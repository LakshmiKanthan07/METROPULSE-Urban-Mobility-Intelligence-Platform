"""
METROPULSE — Congestion Analysis
Computes load-per-train ratios, congestion scores, and peak detection.
"""
import logging

import numpy as np
import pandas as pd

from src.config.settings import DATA_CSV
from src.pipeline.run_pipeline import load_dataset

logger = logging.getLogger(__name__)


def run_congestion_analysis() -> dict[str, pd.DataFrame]:
    """
    Compute congestion metrics:
    - Passengers per train (load / frequency)
    - Congestion classification (Low / Moderate / High / Critical)
    - Peak hour identification
    """
    results = {}

    # ── 1. Load per train (link level) ──────────────────────────────────────
    try:
        loads = load_dataset("tube_link_loads")
        freqs = load_dataset("tube_link_frequencies")

        # Merge on link identifiers + metadata
        merge_keys = ["link", "line", "direction", "from_station", "to_station",
                      "year", "day_type"]

        # Use period-level totals (non-interval rows)
        load_period = (
            loads[loads["time_interval"].isna() | (loads["time_interval"] == "nan")]
            if "time_interval" in loads.columns
            else loads.copy()
        )
        # Actually, the total col has daily totals; am_peak, pm_peak etc have period sums
        # Use the aggregated period columns
        load_agg = (
            loads
            .groupby(merge_keys)[["total", "early", "am_peak", "midday",
                                   "pm_peak", "evening", "late"]]
            .max()
            .reset_index()
        )
        freq_agg = (
            freqs
            .groupby(merge_keys)[["total", "early", "am_peak", "midday",
                                   "pm_peak", "evening", "late"]]
            .max()
            .reset_index()
        )

        # Rename freq columns
        freq_rename = {
            "total": "freq_total", "early": "freq_early",
            "am_peak": "freq_am_peak", "midday": "freq_midday",
            "pm_peak": "freq_pm_peak", "evening": "freq_evening",
            "late": "freq_late",
        }
        freq_agg = freq_agg.rename(columns=freq_rename)

        merged = load_agg.merge(freq_agg, on=merge_keys, how="inner")

        # Passengers per train for each period
        for period in ["total", "early", "am_peak", "midday", "pm_peak", "evening", "late"]:
            freq_col = f"freq_{period}"
            if period == "total":
                load_col = "total"
                out_col  = "pax_per_train_daily"
            else:
                load_col = period
                out_col  = f"pax_per_train_{period}"
            merged[out_col] = merged[load_col] / merged[freq_col].replace(0, np.nan)

        # Congestion classification based on AM Peak load per train
        merged["congestion_class"] = pd.cut(
            merged["pax_per_train_am_peak"].fillna(0),
            bins=[0, 200, 500, 800, np.inf],
            labels=["Low", "Moderate", "High", "Critical"],
        )

        # Congestion score (normalised 0-100)
        max_ppt = merged["pax_per_train_am_peak"].quantile(0.99)
        merged["congestion_score"] = (
            merged["pax_per_train_am_peak"].clip(upper=max_ppt) / max(max_ppt, 1) * 100
        ).round(1)

        results["link_congestion"] = merged
        merged.to_csv(DATA_CSV / "congestion_link_congestion.csv", index=False)
        logger.info("Link congestion: %d records", len(merged))

    except Exception as exc:
        logger.error("Link congestion analysis failed: %s", exc, exc_info=True)

    # ── 2. Station-level congestion ──────────────────────────────────────────
    try:
        entries = load_dataset("tube_station_entries")
        st_cong = (
            entries
            .groupby(["nlc", "asc", "station", "year", "day_type"])[
                ["total", "am_peak", "pm_peak", "midday"]
            ]
            .max()
            .reset_index()
        )

        # Classify stations by AM peak entries
        st_cong["station_congestion_class"] = pd.cut(
            st_cong["am_peak"].fillna(0),
            bins=[0, 2000, 8000, 20000, np.inf],
            labels=["Low", "Moderate", "High", "Critical"],
        )
        results["station_congestion"] = st_cong
        st_cong.to_csv(DATA_CSV / "congestion_station_congestion.csv", index=False)
        logger.info("Station congestion: %d records", len(st_cong))

    except Exception as exc:
        logger.error("Station congestion failed: %s", exc)

    # ── 3. Time-of-day peak detection ────────────────────────────────────────
    try:
        entries = load_dataset("tube_station_entries")
        time_data = entries[entries["start_minute"] >= 0].copy()
        peak_profile = (
            time_data
            .groupby(["start_minute", "time_interval", "period", "year", "day_type"])
            ["passengers"]
            .sum()
            .reset_index()
            .sort_values(["year", "day_type", "start_minute"])
        )
        # Rolling 4-interval (1-hour) average
        peak_profile["rolling_avg"] = (
            peak_profile
            .groupby(["year", "day_type"])["passengers"]
            .transform(lambda x: x.rolling(4, center=True, min_periods=1).mean())
        )
        results["peak_profile"] = peak_profile
        peak_profile.to_csv(DATA_CSV / "congestion_peak_profile.csv", index=False)
        logger.info("Peak profile: %d records", len(peak_profile))

    except Exception as exc:
        logger.error("Peak profile failed: %s", exc)

    return results

