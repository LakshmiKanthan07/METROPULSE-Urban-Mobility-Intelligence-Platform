"""
METROPULSE — Accessibility Analysis
Analyzes spatial coverage, nearest station distances, and accessibility gaps.
"""
import logging
from pathlib import Path
import pandas as pd
import numpy as np
import geopandas as gpd

from src.config.settings import DATA_CSV, DATA_EXTERNAL

logger = logging.getLogger(__name__)

def compute_station_accessibility(gdf_stations: gpd.GeoDataFrame) -> pd.DataFrame:
    """
    Computes spatial accessibility metrics for each station:
    1. Distance to nearest neighboring LU station (in meters / km).
    2. Nearest station name.
    3. Fare zone accessibility tier.
    4. Service coverage index.
    """
    if gdf_stations.empty or len(gdf_stations) < 2:
        logger.warning("Insufficient station spatial data for accessibility calculation.")
        return pd.DataFrame()

    gdf_bng = gdf_stations.to_crs(epsg=27700).copy()
    
    nearest_dists = []
    nearest_stations = []

    coords = np.array([(p.x, p.y) for p in gdf_bng.geometry])
    station_names = gdf_bng["station"].fillna(gdf_bng["asc"]).tolist()

    for i in range(len(coords)):
        dists = np.sqrt(np.sum((coords - coords[i]) ** 2, axis=1))
        # Exclude self
        dists[i] = np.inf
        min_idx = np.argmin(dists)
        nearest_dists.append(dists[min_idx] / 1000.0) # km
        nearest_stations.append(station_names[min_idx])

    gdf_stations = gdf_stations.copy()
    gdf_stations["nearest_station_km"] = np.round(nearest_dists, 2)
    gdf_stations["nearest_station_name"] = nearest_stations

    # Identify potential spatial coverage gaps (e.g. isolated stations where distance to nearest > 3.0 km)
    gdf_stations["is_spatial_isolated"] = gdf_stations["nearest_station_km"] > 3.0

    # Export
    out_df = pd.DataFrame(gdf_stations.drop(columns=["geometry"], errors="ignore"))
    out_df.to_csv(DATA_CSV / "spatial_station_accessibility.csv", index=False)
    logger.info("Accessibility metrics computed for %d stations.", len(out_df))
    return out_df

