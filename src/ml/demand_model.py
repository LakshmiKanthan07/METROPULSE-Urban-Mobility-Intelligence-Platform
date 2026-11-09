"""
METROPULSE — Demand Profile Models
Estimates demand profiles using time-blocked cross-validation
appropriate for NUMBAT typical-day data.
"""
import logging
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.preprocessing import LabelEncoder
import joblib

try:
    from xgboost import XGBRegressor
    HAS_XGB = True
except ImportError:
    HAS_XGB = False

from src.config.settings import DATA_CSV, MODELS_DIR, RANDOM_SEED
from src.pipeline.run_pipeline import load_dataset

logger = logging.getLogger(__name__)


def run_demand_models() -> dict:
    """
    Train and evaluate demand prediction models.
    Target: station daily entries.
    Features: year, day_type, am/pm peak ratios, etc.

    Uses leave-one-year-out cross-validation — appropriate
    because NUMBAT provides one typical-day profile per year/day_type.
    """
    logger.info("Running demand models...")
    MODELS_DIR.mkdir(parents=True, exist_ok=True)

    try:
        df = pd.read_csv(DATA_CSV / "ml_features_station.csv")
    except FileNotFoundError:
        from src.ml.feature_engineering import build_ml_features
        df = build_ml_features()

    if df.empty:
        logger.error("No feature data available for demand models")
        return {}

    # ── Target and legitimate features (Strictly no target leakage) ───────
    target = "ent_total"
    
    df_valid = df.dropna(subset=[target]).copy()
    df_valid = df_valid[df_valid[target] > 0]

    # Encode station as integer
    le = LabelEncoder()
    df_valid["station_enc"] = le.fit_transform(df_valid["asc"].astype(str))
    
    base_features = ["station_enc", "year_norm", "day_type_num", "is_weekend"]

    # ── Leave-one-year-out CV ─────────────────────────────────────────────
    years = sorted(df_valid["year"].unique())
    models = {
        "Ridge":        Ridge(alpha=1.0),
        "RandomForest": RandomForestRegressor(
            n_estimators=100, max_depth=8, random_state=RANDOM_SEED, n_jobs=-1),
        "GBM":          GradientBoostingRegressor(
            n_estimators=100, max_depth=4, random_state=RANDOM_SEED),
    }
    if HAS_XGB:
        models["XGBoost"] = XGBRegressor(
            n_estimators=100, max_depth=4, random_state=RANDOM_SEED,
            verbosity=0, eval_metric="rmse",
        )

    # Seasonal naive baseline
    results = []

    for test_year in years:
        train_mask = df_valid["year"] != test_year
        test_mask  = df_valid["year"] == test_year
        
        train_df = df_valid[train_mask].copy()
        test_df  = df_valid[test_mask].copy()

        if len(train_df) == 0 or len(test_df) == 0:
            continue

        # Historical baseline without leakage
        stn_hist_mean = train_df.groupby("asc")[target].mean()
        train_df["stn_hist_mean"] = train_df["asc"].map(stn_hist_mean)
        test_df["stn_hist_mean"] = test_df["asc"].map(stn_hist_mean).fillna(train_df[target].mean())

        feature_cols = base_features + ["stn_hist_mean"]
        X_train = train_df[feature_cols].values
        y_train = train_df[target].values
        X_test  = test_df[feature_cols].values
        y_test  = test_df[target].values

        # Baseline: mean of training set grouped by station
        y_baseline = test_df["stn_hist_mean"].values

        b_mae  = mean_absolute_error(y_test, y_baseline)
        b_rmse = np.sqrt(mean_squared_error(y_test, y_baseline))
        b_r2   = r2_score(y_test, y_baseline)
        results.append({"model": "SeasonalNaive", "test_year": test_year,
                        "mae": b_mae, "rmse": b_rmse, "r2": b_r2})

        for model_name, model in models.items():
            try:
                model.fit(X_train, y_train)
                y_pred = model.predict(X_test)
                mae  = mean_absolute_error(y_test, y_pred)
                rmse = np.sqrt(mean_squared_error(y_test, y_pred))
                r2   = r2_score(y_test, y_pred)
                results.append({
                    "model": model_name, "test_year": test_year,
                    "mae": mae, "rmse": rmse, "r2": r2,
                })
                logger.info("  %s | test_year=%d | MAE=%.0f RMSE=%.0f R²=%.3f",
                            model_name, test_year, mae, rmse, r2)
            except Exception as exc:
                logger.error("  Model %s failed: %s", model_name, exc)

    results_df = pd.DataFrame(results)
    results_df.to_csv(DATA_CSV / "ml_demand_model_results.csv", index=False)
    logger.info("Demand model results saved.")

    # Save best model (lowest mean MAE)
    if not results_df.empty and len(results_df) > 1:
        avg_mae = results_df.groupby("model")["mae"].mean()
        best_model_name = avg_mae.idxmin()
        logger.info("Best model by MAE: %s (%.0f)", best_model_name, avg_mae.min())

        # Refit best model on all data
        df_valid["stn_hist_mean"] = df_valid["asc"].map(df_valid.groupby("asc")[target].mean())
        feature_cols = base_features + ["stn_hist_mean"]
        X_all = df_valid[feature_cols].values
        y_all = df_valid[target].values

        if best_model_name in models:
            best_model = models[best_model_name]
            best_model.fit(X_all, y_all)
            joblib.dump(best_model, MODELS_DIR / "demand_model_best.pkl")
            joblib.dump(le, MODELS_DIR / "station_label_encoder.pkl")

    # Feature importance for the RandomForest
    if "RandomForest" in models:
        rf = models["RandomForest"]
        rf.fit(X_all, y_all)
        fi = pd.DataFrame({
            "feature": feature_cols,
            "importance": rf.feature_importances_,
        }).sort_values("importance", ascending=False)
        fi.to_csv(DATA_CSV / "ml_feature_importance.csv", index=False)

    return {"results": results_df}

