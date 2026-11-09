"""
METROPULSE — Geospatial Analysis
Spatial demand analysis, network topology, and spatial clustering using GeoPandas.
"""
import logging
from pathlib import Path
import pandas as pd
import numpy as np
import geopandas as gpd
from shapely.geometry import Point, LineString

from src.config.settings import DATA_CSV, DATA_EXTERNAL, REPORTS_DIR
from src.pipeline.run_pipeline import load_dataset
from src.geospatial.station_mapping import fetch_station_coordinates

logger = logging.getLogger(__name__)

# London Centre (Charing Cross / Trafalgar Square) in EPSG:4326
LONDON_CENTRE_LAT = 51.5074
LONDON_CENTRE_LON = -0.1278

def build_station_geodataframe() -> gpd.GeoDataFrame:
    """
    Construct a GeoDataFrame of London Underground stations with coordinates
    projected to British National Grid (EPSG:27700) and WGS84 (EPSG:4326).
    Enriches with passenger entry/exit metrics.
    """
    coords_df = fetch_station_coordinates()
    if coords_df.empty:
        logger.warning("No station coordinates available.")
        return gpd.GeoDataFrame()

    geometry = [Point(xy) for xy in zip(coords_df["lon"], coords_df["lat"])]
    gdf = gpd.GeoDataFrame(coords_df, geometry=geometry, crs="EPSG:4326")
    
    # Project to EPSG:27700 (British National Grid) for meter-based distance calculations
    gdf_bng = gdf.to_crs(epsg=27700)
    
    # Calculate distance from central London (Charing Cross) in km
    centre_pt = gpd.GeoSeries([Point(LONDON_CENTRE_LON, LONDON_CENTRE_LAT)], crs="EPSG:4326").to_crs(epsg=27700).iloc[0]
    gdf["dist_to_centre_km"] = gdf_bng.geometry.distance(centre_pt) / 1000.0

    # Enrich with mean daily entries if available
    try:
        entries = load_dataset("tube_station_entries")
        mean_ent = entries.groupby("asc")["total"].mean().reset_index().rename(columns={"total": "mean_daily_entries"})
        gdf = gdf.merge(mean_ent, on="asc", how="left")
    except Exception as e:
        logger.warning("Could not merge entry metrics: %s", e)

    out_path = DATA_EXTERNAL / "lu_stations_spatial.geojson"
    try:
        gdf.to_file(out_path, driver="GeoJSON")
        logger.info("Saved spatial stations GeoJSON to %s", out_path)
    except Exception as e:
        logger.warning("Could not save GeoJSON directly: %s", e)

    return gdf

def build_network_lines_geodataframe(gdf_stations: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """
    Construct line geometries (LineString) connecting consecutive stations on each LU line.
    """
    try:
        loads = load_dataset("tube_link_loads")
    except Exception:
        logger.warning("Cannot load link loads for line geometries.")
        return gpd.GeoDataFrame()

    if gdf_stations.empty or "asc" not in gdf_stations.columns:
        return gpd.GeoDataFrame()

    coord_dict = dict(zip(gdf_stations["asc"], gdf_stations.geometry))

    links = (
        loads[["line", "from_asc", "to_asc", "from_station", "to_station"]]
        .drop_duplicates()
        .copy()
    )

    lines_records = []
    for _, row in links.iterrows():
        p1 = coord_dict.get(row["from_asc"])
        p2 = coord_dict.get(row["to_asc"])
        if p1 is not None and p2 is not None:
            lines_records.append({
                "line": row["line"],
                "from_station": row["from_station"],
                "to_station": row["to_station"],
                "from_asc": row["from_asc"],
                "to_asc": row["to_asc"],
                "geometry": LineString([p1, p2])
            })

    if not lines_records:
        return gpd.GeoDataFrame()

    gdf_lines = gpd.GeoDataFrame(lines_records, crs="EPSG:4326")
    out_path = DATA_EXTERNAL / "lu_lines_spatial.geojson"
    try:
        gdf_lines.to_file(out_path, driver="GeoJSON")
    except Exception as e:
        logger.warning("Could not write GeoJSON: %s", e)

    return gdf_lines

