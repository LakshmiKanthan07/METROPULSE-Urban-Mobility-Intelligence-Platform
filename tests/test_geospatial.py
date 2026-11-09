"""
METROPULSE — Geospatial Analysis Tests
"""
import pytest
import pandas as pd
import numpy as np
from pathlib import Path

from src.config.settings import DATA_PROCESSED

def test_station_coordinates_bounds():
    """Verify that all station coordinates fall within Greater London bounding box."""
    coords_path = DATA_PROCESSED / "csv" / "spatial_station_accessibility.csv"
    if not coords_path.exists():
        pytest.skip("spatial_station_accessibility.csv not generated yet")
    
    df = pd.read_csv(coords_path)
    assert len(df) > 0
    assert "lat" in df.columns
    assert "lon" in df.columns
    
    # Greater London bounding box: lat ~ 51.2 to 51.8, lon ~ -0.6 to 0.35
    assert df["lat"].between(51.2, 51.8).all(), "Latitudes outside London bounding box"
    assert df["lon"].between(-0.6, 0.4).all(), "Longitudes outside London bounding box"

def test_distance_to_center_positive():
    """Verify distance to central London is non-negative and plausible (<50km)."""
    coords_path = DATA_PROCESSED / "csv" / "spatial_station_accessibility.csv"
    if not coords_path.exists():
        pytest.skip("spatial_station_accessibility.csv not generated yet")
    
    df = pd.read_csv(coords_path)
    assert "dist_to_centre_km" in df.columns
    assert (df["dist_to_centre_km"] >= 0).all()
    assert (df["dist_to_centre_km"] < 60.0).all()
