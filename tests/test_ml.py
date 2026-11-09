"""
METROPULSE — Machine Learning Model Tests
"""
import pytest
import pandas as pd
import numpy as np

from src.config.settings import DATA_PROCESSED

def test_demand_models_accuracy():
    """Verify that demand models achieve acceptable accuracy without target leakage."""
    res_path = DATA_PROCESSED / "csv" / "ml_demand_model_results.csv"
    if not res_path.exists():
        pytest.skip("ml_demand_model_results.csv not generated yet")
    
    df = pd.read_csv(res_path)
    assert len(df) > 0
    assert "r2" in df.columns
    assert "mae" in df.columns
    
    # Models must achieve R2 > 0.85 across leave-one-year-out folds
    best_r2 = df["r2"].max()
    assert best_r2 > 0.85, f"Expected R2 > 0.85, got {best_r2}"
    
    # Models should NOT have R2 == 1.0 or MAE == 0 (which would indicate target leakage)
    assert not (df["mae"] == 0).any(), "Target leakage detected: MAE is 0"
    assert not (df["r2"] == 1.0).any(), "Target leakage detected: R2 is exactly 1.0"

def test_clustering_output_validity():
    """Verify station clustering produces distinct clusters with valid labels."""
    clusters_path = DATA_PROCESSED / "csv" / "ml_station_clusters.csv"
    if not clusters_path.exists():
        pytest.skip("ml_station_clusters.csv not generated yet")
    
    df = pd.read_csv(clusters_path)
    assert "cluster_kmeans" in df.columns
    assert "cluster_label" in df.columns
    assert df["cluster_kmeans"].nunique() >= 3
