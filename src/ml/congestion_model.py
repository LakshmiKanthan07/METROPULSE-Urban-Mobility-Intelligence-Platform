"""
METROPULSE — Congestion Classification Model
Classifies link/station segments into congestion levels.
"""
import logging

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import classification_report, accuracy_score
from sklearn.model_selection import cross_val_score
import joblib

from src.config.settings import DATA_CSV, MODELS_DIR, RANDOM_SEED
from src.pipeline.run_pipeline import load_dataset

logger = logging.getLogger(__name__)


def run_congestion_model() -> dict:
    """
    Train congestion classification model on link data.
    Target: congestion_class (Low / Moderate / High / Critical)
    Uses rule-based labelling from congestion analysis as ground truth.
    """
    logger.info("Running congestion classification model...")
    MODELS_DIR.mkdir(parents=True, exist_ok=True)

    try:
        cong_path = DATA_CSV / "congestion_link_congestion.csv"
        df = pd.read_csv(cong_path)
    except FileNotFoundError:
        logger.warning("Congestion data not found — running congestion analysis first")
        from src.analytics.congestion import run_congestion_analysis
        run_congestion_analysis()
        try:
            df = pd.read_csv(DATA_CSV / "congestion_link_congestion.csv")
        except Exception:
            logger.error("Still cannot load congestion data")
            return {}

    if "congestion_class" not in df.columns:
        logger.error("congestion_class column missing")
        return {}

    df = df.dropna(subset=["congestion_class"])
    df["congestion_class"] = df["congestion_class"].astype(str)

    # Legitimate predictors (Demand volume & scheduled frequency without target ratio leakage)
    feature_cols = [
        "total", "am_peak", "pm_peak", "midday",
        "freq_am_peak", "freq_pm_peak", "freq_total",
    ]
    feature_cols = [c for c in feature_cols if c in df.columns]

    X = df[feature_cols].fillna(0).values
    y = df["congestion_class"].values

    models = {
        "RandomForest": RandomForestClassifier(
            n_estimators=100, random_state=RANDOM_SEED, n_jobs=-1),
        "GBM": GradientBoostingClassifier(
            n_estimators=100, random_state=RANDOM_SEED),
    }

    results = {}
    for name, model in models.items():
        try:
            # 5-fold stratified CV
            scores = cross_val_score(model, X, y, cv=5, scoring="accuracy")
            model.fit(X, y)
            y_pred = model.predict(X)
            report = classification_report(y, y_pred, output_dict=True)
            results[name] = {
                "cv_accuracy_mean": scores.mean(),
                "cv_accuracy_std": scores.std(),
                "classification_report": report,
            }
            logger.info("  %s | CV accuracy: %.3f ± %.3f",
                        name, scores.mean(), scores.std())
        except Exception as exc:
            logger.error("  Model %s failed: %s", name, exc)

    # Save best model
    if results:
        best = max(results, key=lambda m: results[m]["cv_accuracy_mean"])
        models[best].fit(X, y)
        joblib.dump(models[best], MODELS_DIR / "congestion_model_best.pkl")

        # Save predictions
        df["predicted_class"] = models[best].predict(X)
        df.to_csv(DATA_CSV / "ml_congestion_predictions.csv", index=False)

    # Feature importance
    if "RandomForest" in models:
        rf = models["RandomForest"]
        fi = pd.DataFrame({
            "feature": feature_cols,
            "importance": rf.feature_importances_,
        }).sort_values("importance", ascending=False)
        fi.to_csv(DATA_CSV / "ml_congestion_feature_importance.csv", index=False)

    return results

