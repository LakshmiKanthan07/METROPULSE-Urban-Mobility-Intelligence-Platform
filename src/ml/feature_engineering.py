"""
METROPULSE — Feature Engineering for ML
Builds features from processed NUMBAT datasets.
"""
import logging

import numpy as np
import pandas as pd

from src.config.settings import DATA_CSV, RANDOM_SEED
from src.pipeline.run_pipeline import load_dataset

logger = logging.getLogger(__name__)


def build_ml_features() -> pd.DataFrame:
    """
    Build a comprehensive ML feature matrix for demand modelling and clustering.
    One row per station × year × day_type combination.
    """
    logger.info("Building ML feature matrix...")

    try:
        entries  = load_dataset("tube_station_entries")
        exits    = load_dataset("tube_station_exits")
        boarders = load_dataset("tube_station_boarders")
        alighters= load_dataset("tube_station_alighters")

        # ── Station-level daily features ──────────────────────────────────
        ent = (
            entries
            .groupby(["nlc", "asc", "station", "year", "day_type"])[
                ["total", "early", "am_peak", "midday", "pm_peak", "evening", "late"]
            ].max().reset_index()
            .rename(columns=lambda c: f"ent_{c}" if c not in
                    ["nlc","asc","station","year","day_type"] else c)
        )

        ext = (
            exits
            .groupby(["nlc", "asc", "station", "year", "day_type"])[
                ["total", "early", "am_peak", "midday", "pm_peak", "evening", "late"]
            ].max().reset_index()
            .rename(columns=lambda c: f"ext_{c}" if c not in
                    ["nlc","asc","station","year","day_type"] else c)
        )

        brd = (
            boarders
            .groupby(["nlc", "asc", "station", "year", "day_type"])[
                ["total", "am_peak", "pm_peak"]
            ].sum().reset_index()
            .rename(columns=lambda c: f"brd_{c}" if c not in
                    ["nlc","asc","station","year","day_type"] else c)
        )

        ali = (
            alighters
            .groupby(["nlc", "asc", "station", "year", "day_type"])[
                ["total", "am_peak", "pm_peak"]
            ].sum().reset_index()
            .rename(columns=lambda c: f"ali_{c}" if c not in
                    ["nlc","asc","station","year","day_type"] else c)
        )

        # Merge
        df = ent.merge(ext, on=["nlc","asc","station","year","day_type"], how="outer")
        df = df.merge(brd, on=["nlc","asc","station","year","day_type"], how="outer")
        df = df.merge(ali, on=["nlc","asc","station","year","day_type"], how="outer")

        # ── Derived features ──────────────────────────────────────────────
        df["net_flow"]       = df["ent_total"].fillna(0) - df["ext_total"].fillna(0)
        df["am_peak_ratio"]  = df["ent_am_peak"] / df["ent_total"].replace(0, np.nan)
        df["pm_peak_ratio"]  = df["ent_pm_peak"] / df["ent_total"].replace(0, np.nan)
        df["peak_asymmetry"] = df["ent_am_peak"].fillna(0) - df["ent_pm_peak"].fillna(0)
        df["boarder_ratio"]  = df["brd_total"] / df["ent_total"].replace(0, np.nan)

        # Categorical features
        df["day_type_num"]   = df["day_type"].map(
            {"MON": 0, "TWT": 1, "FRI": 2, "SAT": 3, "SUN": 4}
        ).fillna(2)
        df["is_weekend"]     = df["day_type"].isin(["SAT", "SUN"]).astype(int)
        df["year_norm"]      = df["year"] - 2023  # 0, 1, 2

        # Fill NaN with 0 for numeric cols
        num_cols = df.select_dtypes(include=np.number).columns
        df[num_cols] = df[num_cols].fillna(0)

        out_path = DATA_CSV / "ml_features_station.csv"
        df.to_csv(out_path, index=False)
        logger.info("ML features saved: %d rows × %d cols → %s",
                    len(df), len(df.columns), out_path)
        return df

    except Exception as exc:
        logger.error("Feature engineering failed: %s", exc, exc_info=True)
        return pd.DataFrame()

