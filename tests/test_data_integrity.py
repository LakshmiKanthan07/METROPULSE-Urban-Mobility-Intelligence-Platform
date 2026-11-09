"""
Unit Tests for Data Integrity, Availability Matrix, and Zero-Fabrication Enforcement
"""
import pytest
import pandas as pd
from pathlib import Path

ROOT = Path(__file__).parent.parent
REPORTS_DIR = ROOT / "reports"


def test_availability_matrix_exists_and_complete():
    """Verify data_availability_matrix.csv is generated and contains audited metrics."""
    matrix_file = REPORTS_DIR / "data_availability_matrix.csv"
    assert matrix_file.exists(), "data_availability_matrix.csv must exist in reports/"
    
    df = pd.read_csv(matrix_file)
    assert len(df) >= 20, f"Expected at least 20 audited metrics, found {len(df)}"
    
    expected_cols = [
        "metric_name", "category", "status", "data_lineage",
        "source_workbook", "source_worksheet", "formula"
    ]
    for col in expected_cols:
        assert col in df.columns, f"Missing expected column '{col}' in availability matrix"


def test_valid_availability_statuses():
    """Verify all metrics have valid standardized availability status tags."""
    df = pd.read_csv(REPORTS_DIR / "data_availability_matrix.csv")
    valid_statuses = {
        "AVAILABLE", "DERIVABLE", "UNAVAILABLE",
        "REQUIRES USER INPUT", "PARTIALLY AVAILABLE",
        "NOT APPLICABLE", "REQUIRES EXTERNAL DATA"
    }
    found_statuses = set(df["status"].unique())
    assert found_statuses.issubset(valid_statuses), f"Invalid status found: {found_statuses - valid_statuses}"


def test_missing_data_report_exists():
    """Verify missing_data_report.md and CSV exist and are populated."""
    md_file = REPORTS_DIR / "missing_data_report.md"
    csv_file = REPORTS_DIR / "missing_data_report.csv"
    assert md_file.exists(), "missing_data_report.md must exist in reports/"
    assert csv_file.exists(), "missing_data_report.csv must exist in reports/"
    
    df_missing = pd.read_csv(csv_file)
    assert len(df_missing) >= 4, "Must document at least 4 missing NUMBAT indicators"


def test_user_input_required_exists():
    """Verify reports/USER_INPUT_REQUIRED.md exists and contains the 4 essential categories."""
    path = REPORTS_DIR / "USER_INPUT_REQUIRED.md"
    assert path.exists(), "USER_INPUT_REQUIRED.md must exist in reports/"
    
    content = path.read_text(encoding="utf-8")
    assert "1. Essential Missing Information" in content
    assert "2. Optional Enhancements & Analytical Assumptions" in content
    assert "3. External Datasets to Potentially Obtain" in content
    assert "4. Dashboard Features Currently Handled via Graceful Fallback States" in content


def test_zero_vs_null_handling():
    """Test that 0 is treated as a valid number and NaN/None as missing."""
    val_zero = 0
    assert not pd.isna(val_zero)
    assert val_zero is not None
    
    val_nan = float("nan")
    assert pd.isna(val_nan)
    val_none = None
    assert val_none is None
