"""
METROPULSE — Station Clustering
Groups stations by demand patterns using KMeans, DBSCAN, Hierarchical.
"""
import logging

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans, DBSCAN, AgglomerativeClustering
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score
import joblib

from src.config.settings import DATA_CSV, MODELS_DIR, RANDOM_SEED

logger = logging.getLogger(__name__)

# Cluster semantic labels (assigned after inspecting cluster profiles)
CLUSTER_LABELS_DEFAULT = {
    0: "Major Interchange Hub",
    1: "High-Demand Commuter",
    2: "Residential Feeder",
    3: "Low-Demand Peripheral",
    4: "Weekend-Oriented",
}


def run_clustering() -> pd.DataFrame:
    """
    Cluster London Underground stations by demand profile.
    Uses weekday (MON) data as the representative profile.
    """
    logger.info("Running station clustering...")
    MODELS_DIR.mkdir(parents=True, exist_ok=True)

    try:
        df = pd.read_csv(DATA_CSV / "ml_features_station.csv")
    except FileNotFoundError:
        from src.ml.feature_engineering import build_ml_features
        df = build_ml_features()

    # Use Monday 2024 as reference day
    ref = df[(df["day_type"] == "MON") & (df["year"] == 2024)].copy()
    if ref.empty:
        ref = df[df["day_type"] == "MON"].copy()
    if ref.empty:
        ref = df.copy()

    feature_cols = [
        "ent_total", "ent_am_peak", "ent_pm_peak", "ent_midday",
        "ent_early", "ent_evening", "am_peak_ratio", "pm_peak_ratio",
        "peak_asymmetry", "net_flow",
    ]
    feature_cols = [c for c in feature_cols if c in ref.columns]

    X = ref[feature_cols].fillna(0).values
    if len(X) < 10:
        logger.warning("Too few stations for clustering")
        return pd.DataFrame()

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # ── KMeans with optimal k ─────────────────────────────────────────────
    best_k, best_sil = 4, -1
    for k in range(3, 8):
        km = KMeans(n_clusters=k, random_state=RANDOM_SEED, n_init=10)
        labels = km.fit_predict(X_scaled)
        try:
            sil = silhouette_score(X_scaled, labels)
            if sil > best_sil:
                best_k, best_sil = k, sil
        except Exception:
            pass

    km_best = KMeans(n_clusters=best_k, random_state=RANDOM_SEED, n_init=10)
    ref["cluster_kmeans"] = km_best.fit_predict(X_scaled)
    logger.info("KMeans: k=%d, silhouette=%.3f", best_k, best_sil)

    # ── DBSCAN ───────────────────────────────────────────────────────────
    db = DBSCAN(eps=0.8, min_samples=3)
    ref["cluster_dbscan"] = db.fit_predict(X_scaled)
    n_dbscan = len(set(ref["cluster_dbscan"])) - (1 if -1 in ref["cluster_dbscan"].values else 0)
    logger.info("DBSCAN: %d clusters, %d noise points",
                n_dbscan, (ref["cluster_dbscan"] == -1).sum())

    # ── Hierarchical ─────────────────────────────────────────────────────
    hc = AgglomerativeClustering(n_clusters=best_k)
    ref["cluster_hierarchical"] = hc.fit(X_scaled).labels_

    # ── Profile cluster means ─────────────────────────────────────────────
    cluster_profiles = (
        ref.groupby("cluster_kmeans")[feature_cols]
        .mean()
        .reset_index()
    )

    # Assign semantic labels (heuristic based on total demand and peak ratio)
    # Sort clusters by total demand descending
    cluster_profiles = cluster_profiles.sort_values(
        "ent_total" if "ent_total" in cluster_profiles.columns else feature_cols[0],
        ascending=False,
    ).reset_index(drop=True)
    label_map = {
        int(row["cluster_kmeans"]): list(CLUSTER_LABELS_DEFAULT.values())[i]
        for i, (_, row) in enumerate(cluster_profiles.iterrows())
        if i < len(CLUSTER_LABELS_DEFAULT)
    }
    ref["cluster_label"] = ref["cluster_kmeans"].map(label_map).fillna("Other")

    # Save
    out_cols = ["nlc", "asc", "station", "year", "day_type",
                "cluster_kmeans", "cluster_dbscan", "cluster_hierarchical", "cluster_label"]
    out_cols = [c for c in out_cols if c in ref.columns]
    result = ref[out_cols].reset_index(drop=True)
    result.to_csv(DATA_CSV / "ml_station_clusters.csv", index=False)
    cluster_profiles.to_csv(DATA_CSV / "ml_cluster_profiles.csv", index=False)

    joblib.dump(km_best, MODELS_DIR / "kmeans_clustering.pkl")
    joblib.dump(scaler,  MODELS_DIR / "cluster_scaler.pkl")

    logger.info("Clustering complete: %d stations, %d clusters", len(result), best_k)
    return result

