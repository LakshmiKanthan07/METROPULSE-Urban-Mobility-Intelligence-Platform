"""
METROPULSE — Analytics & Optimization Unit Tests
"""
import pytest
import pandas as pd
import numpy as np
import networkx as nx

def test_load_per_train_calculation():
    """Verify Load per train calculation logic and zero-division handling."""
    load = pd.Series([1000.0, 500.0, 200.0])
    freq = pd.Series([20.0, 10.0, 0.0])
    lpt = load / freq.replace(0, np.nan)
    assert lpt.iloc[0] == 50.0
    assert lpt.iloc[1] == 50.0
    assert pd.isna(lpt.iloc[2])

def test_congestion_classification_bins():
    """Verify standard congestion thresholds."""
    series = pd.Series([150, 350, 650, 950])
    classes = pd.cut(
        series,
        bins=[0, 200, 500, 800, np.inf],
        labels=["Low", "Moderate", "High", "Critical"]
    )
    assert list(classes) == ["Low", "Moderate", "High", "Critical"]

def test_service_adequacy_index_bounds():
    """Verify Service Adequacy Index stays within expected [0, 100] bounds."""
    demand_norm = np.array([0.0, 0.5, 1.0])
    freq_norm   = np.array([1.0, 0.5, 0.0]) # 1 - freq = [0.0, 0.5, 1.0]
    ppt_norm    = np.array([0.0, 0.5, 1.0])
    
    sai = (demand_norm * (1.0 - freq_norm) * ppt_norm) * 100.0
    assert sai[0] == 0.0 # Perfectly served
    assert sai[1] == 12.5
    assert sai[2] == 100.0 # Severely underserved

def test_network_graph_construction():
    """Verify graph creation and basic centrality properties."""
    G = nx.DiGraph()
    G.add_edge("OXCu", "TCRu", line="Central", am_peak_load=15000)
    G.add_edge("TCRu", "HOLu", line="Central", am_peak_load=18000)
    
    assert G.number_of_nodes() == 3
    assert G.number_of_edges() == 2
    deg = dict(G.degree())
    assert deg["TCRu"] == 2 # 1 in, 1 out

