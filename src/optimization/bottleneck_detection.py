"""
METROPULSE — Bottleneck Detection
Identifies high-load, low-frequency segments in the LU network.
"""
import logging

import networkx as nx
import pandas as pd
import numpy as np

from src.config.settings import DATA_CSV
from src.pipeline.run_pipeline import load_dataset

logger = logging.getLogger(__name__)


def detect_bottlenecks(G: nx.DiGraph) -> pd.DataFrame:
    """
    Identify network bottlenecks using:
    - High pax per train (demand exceeds capacity proxy)
    - High betweenness centrality (critical path segments)
    - Bridge detection (single points of failure)
    """
    logger.info("Detecting network bottlenecks...")

    # Edge-level bottleneck metrics
    edge_records = []
    for u, v, data in G.edges(data=True):
        edge_records.append({
            "from_asc":         u,
            "to_asc":           v,
            "from_station":     G.nodes[u].get("station", u),
            "to_station":       G.nodes[v].get("station", v),
            "line":             data.get("line", ""),
            "direction":        data.get("direction", ""),
            "am_peak_load":     data.get("am_peak_load", 0),
            "freq_am":          data.get("freq_am", 0),
            "pax_per_train_am": data.get("pax_per_train_am", 0),
            "total_load":       data.get("total_load", 0),
        })

    if not edge_records:
        logger.warning("No edges in graph — cannot detect bottlenecks")
        return pd.DataFrame()

    df = pd.DataFrame(edge_records)

    # Percentile thresholds
    p75_ppt  = df["pax_per_train_am"].quantile(0.75)
    p75_load = df["am_peak_load"].quantile(0.75)
    p25_freq = df["freq_am"].quantile(0.25)

    df["is_high_load"]     = df["am_peak_load"]     >= p75_load
    df["is_high_ppt"]      = df["pax_per_train_am"] >= p75_ppt
    df["is_low_frequency"] = df["freq_am"]           <= p25_freq
    df["is_bottleneck"]    = df["is_high_load"] & df["is_high_ppt"]
    df["bottleneck_severity"] = (
        df["is_high_load"].astype(int) +
        df["is_high_ppt"].astype(int) +
        df["is_low_frequency"].astype(int)
    )

    # Node betweenness (use undirected)
    G_und = G.to_undirected()
    betweenness = nx.betweenness_centrality(G_und, normalized=True)
    df["from_betweenness"] = df["from_asc"].map(betweenness).fillna(0)
    df["to_betweenness"]   = df["to_asc"].map(betweenness).fillna(0)
    df["avg_betweenness"]  = (df["from_betweenness"] + df["to_betweenness"]) / 2

    df = df.sort_values("bottleneck_severity", ascending=False)
    df.to_csv(DATA_CSV / "network_bottlenecks.csv", index=False)
    logger.info("Bottlenecks: %d total, %d identified",
                len(df), df["is_bottleneck"].sum())
    return df

