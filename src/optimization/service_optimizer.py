"""
METROPULSE — Service Optimizer
Models service improvement scenarios for the LU network.
"""
import logging

import networkx as nx
import pandas as pd
import numpy as np

from src.config.settings import DATA_CSV

logger = logging.getLogger(__name__)


def run_optimization_scenarios(G: nx.DiGraph) -> pd.DataFrame:
    """
    Model two scenarios:
        BASELINE: Current service frequencies
        IMPROVED:  +25% frequency on bottleneck links

    Computes estimated change in passengers per train.
    Does NOT claim to produce a deployable timetable.
    Documents all assumptions explicitly.
    """
    logger.info("Running service optimization scenarios...")

    try:
        bottlenecks = pd.read_csv(DATA_CSV / "network_bottlenecks.csv")
    except FileNotFoundError:
        logger.warning("Bottleneck data not found")
        return pd.DataFrame()

    scenarios = []
    for _, row in bottlenecks.iterrows():
        link_desc = f"{row.get('from_station','')} → {row.get('to_station','')}"
        ppt_base  = row.get("pax_per_train_am", 0) or 0
        freq_base = row.get("freq_am", 0) or 0
        load      = row.get("am_peak_load", 0) or 0

        # SCENARIO A: +25% frequency for bottleneck links
        if row.get("is_bottleneck") and freq_base > 0:
            freq_improved = freq_base * 1.25
            ppt_improved  = load / freq_improved
            improvement_pct = (ppt_base - ppt_improved) / max(ppt_base, 1) * 100
        else:
            freq_improved   = freq_base
            ppt_improved    = ppt_base
            improvement_pct = 0.0

        scenarios.append({
            "link":             row.get("link", ""),
            "from_station":     row.get("from_station", ""),
            "to_station":       row.get("to_station", ""),
            "line":             row.get("line", ""),
            "direction":        row.get("direction", ""),
            "am_peak_load":     load,
            "freq_baseline":    freq_base,
            "freq_improved":    round(freq_improved, 1),
            "ppt_baseline":     round(ppt_base, 1),
            "ppt_improved":     round(ppt_improved, 1),
            "ppt_reduction_pct": round(improvement_pct, 1),
            "is_bottleneck":    row.get("is_bottleneck", False),
            "scenario":         "FreqIncrease+25%",
            "assumption":       (
                "Assumes +25% train frequency is operationally feasible; "
                "no infrastructure constraints modelled; "
                "demand assumed constant (no induced demand)."
            ),
        })

    df = pd.DataFrame(scenarios)
    df = df.sort_values("ppt_reduction_pct", ascending=False)
    df.to_csv(DATA_CSV / "optimization_scenarios.csv", index=False)
    logger.info("Optimization scenarios: %d links analysed", len(df))
    return df

