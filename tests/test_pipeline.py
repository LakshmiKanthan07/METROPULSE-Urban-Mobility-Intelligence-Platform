"""
METROPULSE — Comprehensive Unit & Integration Tests
Pytest suite for verification of data engineering, filtering, analytics, ML, and dashboard utilities.
"""
import pytest
from pathlib import Path
import pandas as pd
import numpy as np

from src.config.settings import DATA_RAW, LU_LINE_CODES, LU_MODE_CODE
from src.ingestion.workbook_reader import discover_files, list_sheets
from src.preprocessing.mode_filter import filter_lu
from src.preprocessing.standardization import parse_time_interval_to_minutes
from src.preprocessing.cleaning import normalise_direction, add_period_label, clean_common
from src.preprocessing.validation import validate_dataset

# ── 1. Ingestion & File Discovery Tests ───────────────────────────────────────
def test_discover_files():
    """Verify that all 15 raw Excel workbooks are discovered."""
    files = discover_files(DATA_RAW)
    assert len(files) == 15, f"Expected 15 workbooks, found {len(files)}"
    
    years = {f["year"] for f in files}
    assert years == {2023, 2024, 2025}, f"Unexpected years: {years}"
    
    day_types = {f["day_type_code"] for f in files}
    assert day_types == {"FRI", "MON", "SAT", "SUN", "TWT"}, f"Unexpected day types: {day_types}"

def test_worksheet_discovery():
    """Verify that key worksheets exist in sample workbooks."""
    files = discover_files(DATA_RAW)
    assert len(files) > 0
    sample_file = files[0]["path"]
    sheets = list_sheets(sample_file)
    expected = {"Link_Loads", "Link_Frequencies", "Line_Boarders", "Station_Entries", "Station_Exits"}
    assert expected.issubset(set(sheets)), f"Missing expected sheets in {sample_file.name}"

# ── 2. Mode Filtering Tests ──────────────────────────────────────────────────
def test_filter_lu_line_boarders():
    """Verify that only LU records are retained from Line_Boarders."""
    mock_data = pd.DataFrame({
        "Mode": ["LU", "LU", "DLR", "LO", "EZL", "TRM"],
        "Line Code": ["BAK", "CEN", "DLR", "NLL", "EZL", "TRM"],
        "Total": [100, 200, 50, 60, 80, 0]
    })
    filtered = filter_lu(mock_data, "Line_Boarders")
    assert len(filtered) == 2
    assert set(filtered["Line Code"]) == {"BAK", "CEN"}
    assert (filtered["Mode"] == "LU").all()

def test_filter_lu_station_entries():
    """Verify that ASC codes ending with 'u' (LU stations) are isolated."""
    mock_data = pd.DataFrame({
        "ASC": ["ACTu", "WLOu", "ABRd", "ACCr", "AMLr", "KGXu"],
        "Station": ["Acton Town", "Waterloo", "Abbey Road", "Acton Central", "Acton Main Line", "King's Cross"],
        "Total": [5000, 25000, 1000, 1500, 2000, 45000]
    })
    filtered = filter_lu(mock_data, "Station_Entries")
    assert len(filtered) == 3
    assert set(filtered["ASC"]) == {"ACTu", "WLOu", "KGXu"}

def test_filter_lu_link_loads():
    """Verify LU link loads retain only Underground lines."""
    mock_data = pd.DataFrame({
        "Line": ["Bakerloo", "Central", "DLR", "Elizabeth Line", "Victoria"],
        "Link": ["ELEu_BAK_NB>LAMu", "OXCu_CEN_EB>TOTu", "DLR_link", "EZL_link", "VIC_link"],
        "Total": [1000, 2000, 500, 3000, 2500]
    })
    filtered = filter_lu(mock_data, "Link_Loads")
    assert len(filtered) == 3
    assert set(filtered["Line"]) == {"Bakerloo", "Central", "Victoria"}

# ── 3. Cleaning & Normalization Tests ─────────────────────────────────────────
def test_time_interval_parsing():
    """Test conversion of 15-minute string interval to start minutes."""
    assert parse_time_interval_to_minutes("0500-0515") == 300
    assert parse_time_interval_to_minutes("0830-0845") == 510
    assert parse_time_interval_to_minutes("1745-1800") == 1065
    assert parse_time_interval_to_minutes("invalid") == -1

def test_direction_normalization():
    """Test direction standardization."""
    df = pd.DataFrame({"direction": ["nb", " sb ", "Eb", "wb"]})
    norm = normalise_direction(df)
    assert list(norm["direction"]) == ["NB", "SB", "EB", "WB"]

def test_period_labeling():
    """Test 15-minute interval to period mapping."""
    df = pd.DataFrame({"time_interval": ["0515-0530", "0745-0800", "1230-1245", "1715-1730", "2000-2015", "2315-2330"]})
    labeled = add_period_label(df)
    assert list(labeled["period"]) == ["Early", "AM Peak", "Midday", "PM Peak", "Evening", "Late"]

def test_clean_common_negative_clipping():
    """Test that negative passenger values (rounding noise) are safely clipped to 0."""
    df = pd.DataFrame({"total": [100.0, -0.05, 50.0], "station": ["A", "B", "C"]})
    cleaned = clean_common(df)
    assert (cleaned["total"] >= 0).all()
    assert cleaned.loc[cleaned["station"] == "B", "total"].iloc[0] == 0.0

# ── 4. Validation & Quality Checks ───────────────────────────────────────────
def test_dataset_validation():
    """Test quality check summary output."""
    df = pd.DataFrame({
        "link": ["L1", "L2"],
        "line_code": ["BAK", "CEN"],
        "total": [1000.0, 500.0],
        "year": [2024, 2024],
        "day_type": ["MON", "MON"]
    })
    res = validate_dataset(df, "test_set", expected_line_codes=LU_LINE_CODES)
    assert res["total_rows"] == 2
    assert res["duplicate_rows"] == 0
    assert res["negative_passengers"] == 0
    assert res["invalid_line_codes"] == 0
    assert not res["has_critical_issues"]

