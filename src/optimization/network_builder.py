"""
METROPULSE — Network Builder
Constructs a NetworkX graph of the London Underground network.
"""
import logging

import networkx as nx
import pandas as pd

from src.config.settings import DATA_CSV
from src.pipeline.run_pipeline import load_dataset

logger = logging.getLogger(__name__)


def build_network(year: int = 2024, day_type: str = "MON") -> nx.DiGraph:
    """
    Build a directed graph of the LU network.

    Nodes: stations (identified by ASC code)
    Edges: directed link between consecutive stations

    Edge attributes:
        line, direction, order, total_load, am_peak_load,
        freq_am_peak, pax_per_train_am, congestion_score
    """
    logger.info("Building LU network graph (year=%d, day=%s)...", year, day_type)

    loads = load_dataset("tube_link_loads")
    freqs = load_dataset("tube_link_frequencies")

    # Filter to specified year/day
    loads_f = loads[(loads["year"] == year) & (loads["day_type"] == day_type)]
    freqs_f = freqs[(freqs["year"] == year) & (freqs["day_type"] == day_type)]

    if loads_f.empty:
        logger.warning("No link load data for year=%d, day=%s", year, day_type)
        loads_f = loads

    # Aggregate: take max total per link (handles duplicate rows from melt)
    merge_keys = ["link", "line", "direction", "from_asc", "from_station",
                  "to_asc", "to_station", "order"]
    mk_loads = [k for k in merge_keys if k in loads_f.columns]

    load_agg = (
        loads_f.groupby(mk_loads)[["total", "am_peak", "pm_peak"]]
        .max().reset_index()
    )

    freq_cols = [k for k in merge_keys if k in freqs_f.columns]
    freq_agg = (
        freqs_f.groupby(freq_cols)[["total", "am_peak"]]
        .max().reset_index()
        .rename(columns={"total": "freq_total", "am_peak": "freq_am"})
    )

    merged = load_agg.merge(freq_agg, on=mk_loads, how="left")
    merged["pax_per_train_am"] = (
        merged["am_peak"] / merged["freq_am"].replace(0, float("nan"))
    )

    # Build graph
    G = nx.DiGraph()

    for _, row in merged.iterrows():
        from_node = str(row.get("from_asc", row.get("from_station", "")))
        to_node   = str(row.get("to_asc",   row.get("to_station",   "")))

        if not from_node or not to_node or from_node == "nan" or to_node == "nan":
            continue

        # Add nodes with station label
        if not G.has_node(from_node):
            G.add_node(from_node,
                       station=str(row.get("from_station", from_node)),
                       asc=from_node)
        if not G.has_node(to_node):
            G.add_node(to_node,
                       station=str(row.get("to_station", to_node)),
                       asc=to_node)

        G.add_edge(
            from_node, to_node,
            link=str(row.get("link", "")),
            line=str(row.get("line", "")),
            direction=str(row.get("direction", "")),
            order=int(row.get("order", 0)) if pd.notna(row.get("order")) else 0,
            total_load=float(row.get("total", 0) or 0),
            am_peak_load=float(row.get("am_peak", 0) or 0),
            freq_am=float(row.get("freq_am", 0) or 0),
            pax_per_train_am=float(row.get("pax_per_train_am", 0) or 0),
        )

    logger.info("Network: %d nodes, %d edges", G.number_of_nodes(), G.number_of_edges())
    return G


def compute_centrality(G: nx.DiGraph) -> pd.DataFrame:
    """Compute degree, betweenness, and closeness centrality."""
    logger.info("Computing network centrality...")

    # Undirected for centrality calculations
    G_und = G.to_undirected()

    degree = dict(G_und.degree(weight="am_peak_load"))
    betweenness = nx.betweenness_centrality(G_und, weight="am_peak_load",
                                             normalized=True)
    try:
        closeness = nx.closeness_centrality(G_und)
    except Exception:
        closeness = {n: 0.0 for n in G_und.nodes()}

    records = []
    for node in G.nodes():
        records.append({
            "asc":               node,
            "station":           G.nodes[node].get("station", node),
            "degree":            degree.get(node, 0),
            "betweenness":       round(betweenness.get(node, 0), 6),
            "closeness":         round(closeness.get(node, 0), 6),
            "in_degree":         G.in_degree(node),
            "out_degree":        G.out_degree(node),
        })

    centrality_df = pd.DataFrame(records).sort_values("betweenness", ascending=False)
    centrality_df.to_csv(DATA_CSV / "network_centrality.csv", index=False)
    logger.info("Centrality saved: %d nodes", len(centrality_df))
    return centrality_df

