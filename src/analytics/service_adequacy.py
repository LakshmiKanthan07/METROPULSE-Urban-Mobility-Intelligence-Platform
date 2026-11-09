"""
METROPULSE — Service Adequacy Analysis
Builds the Service Adequacy Index (SAI) comparing demand to frequency.
"""
import logging

import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler

from src.config.settings import DATA_CSV
from src.pipeline.run_pipeline import load_dataset

logger = logging.getLogger(__name__)


def run_service_adequacy() -> pd.DataFrame:
    """
    Build Service Adequacy Index:
        SAI = weighted composite of normalised:
              1. passengers per train (inverted — higher is worse)
              2. service frequency (direct — more is better)
              3. demand magnitude (entries total)

    Returns scored DataFrame.
    """
    try:
        loads = load_dataset("tube_link_loads")
        freqs = load_dataset("tube_link_frequencies")

        merge_keys = ["link", "line", "direction", "from_station", "to_station",
                      "year", "day_type"]

        load_agg = (
            loads.groupby(merge_keys)
            [["total", "am_peak", "pm_peak"]]
            .max().reset_index()
        )
        freq_agg = (
            freqs.groupby(merge_keys)
            [["total", "am_peak", "pm_peak"]]
            .max().reset_index()
            .rename(columns={"total": "freq_total",
                             "am_peak": "freq_am",
                             "pm_peak": "freq_pm"})
        )

        df = load_agg.merge(freq_agg, on=merge_keys, how="inner")

        # Passengers per train (AM peak)
        df["ppt_am"] = df["am_peak"] / df["freq_am"].replace(0, np.nan)
        df["ppt_pm"] = df["pm_peak"] / df["freq_pm"].replace(0, np.nan)

        # Normalise features (0-1) using MinMaxScaler
        scaler = MinMaxScaler()
        feature_cols = ["ppt_am", "freq_am", "total"]
        df_feat = df[feature_cols].fillna(0)
        normed = pd.DataFrame(
            scaler.fit_transform(df_feat),
            columns=["ppt_am_norm", "freq_am_norm", "demand_norm"],
        )
        df = pd.concat([df.reset_index(drop=True), normed], axis=1)

        # SAI: high demand + low frequency = low adequacy
        # SAI = demand_norm * (1 - freq_am_norm) * ppt_am_norm
        # Score 0 (adequate) → 100 (severely inadequate)
        df["service_adequacy_index"] = (
            (df["demand_norm"] * (1 - df["freq_am_norm"]) * df["ppt_am_norm"]) * 100
        ).round(2)

        # Categorise
        df["adequacy_class"] = pd.cut(
            df["service_adequacy_index"],
            bins=[0, 10, 30, 60, 100],
            labels=["Well Served", "Adequate", "Underserved", "Severely Underserved"],
            include_lowest=True,
        )

        df.to_csv(DATA_CSV / "service_adequacy.csv", index=False)
        logger.info("Service adequacy: %d link records", len(df))
        return df

    except Exception as exc:
        logger.error("Service adequacy failed: %s", exc, exc_info=True)
        return pd.DataFrame()

