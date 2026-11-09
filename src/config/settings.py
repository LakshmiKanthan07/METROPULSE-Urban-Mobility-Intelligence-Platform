"""
METROPULSE — Urban Mobility Intelligence Platform
Central configuration settings.
"""
import os
from pathlib import Path

# ─── Project Root ────────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# ─── Data Directories ────────────────────────────────────────────────────────
DATA_RAW       = PROJECT_ROOT / "data" / "raw"
DATA_INTERIM   = PROJECT_ROOT / "data" / "interim"
DATA_PROCESSED = PROJECT_ROOT / "data" / "processed"
DATA_CSV       = DATA_PROCESSED / "csv"
DATA_PARQUET   = DATA_PROCESSED / "parquet"
DATA_EXTERNAL  = PROJECT_ROOT / "data" / "external"
DATA_BI        = PROJECT_ROOT / "data" / "bi_exports"

# ─── Output Directories ──────────────────────────────────────────────────────
NOTEBOOKS_DIR  = PROJECT_ROOT / "notebooks"
REPORTS_DIR    = PROJECT_ROOT / "reports"
FIGURES_DIR    = REPORTS_DIR / "figures"
DQ_REPORTS_DIR = REPORTS_DIR / "data_quality"
MODELS_DIR     = PROJECT_ROOT / "models"
LOGS_DIR       = PROJECT_ROOT / "logs"
DOCS_DIR       = PROJECT_ROOT / "docs"

# ─── Worksheet Names ─────────────────────────────────────────────────────────
WORKSHEETS = [
    "Link_Loads",
    "Link_Frequencies",
    "Line_Boarders",
    "Station_Flows",
    "Station_Entries",
    "Station_Exits",
    "Station_Boarders",
    "Station_Alighters",
    "_Cover",
    "LineLookUp",
]

# ─── London Underground Line Codes ───────────────────────────────────────────
LU_LINE_CODES = {"BAK", "CEN", "DIS", "HAM", "JUB", "MET", "NOR", "PIC", "VIC", "WAC"}
LU_LINE_NAMES = {
    "BAK": "Bakerloo",
    "CEN": "Central",
    "DIS": "District",
    "HAM": "H&C and Circle",
    "JUB": "Jubilee",
    "MET": "Metropolitan",
    "NOR": "Northern",
    "PIC": "Piccadilly",
    "VIC": "Victoria",
    "WAC": "Waterloo & City",
}
LU_MODE_CODE = "LU"

# ─── ASC suffix codes that indicate LU stations ──────────────────────────────
LU_ASC_SUFFIX = "u"   # e.g. ACTu, WLOu, KGXu

# ─── Day Type Mapping ────────────────────────────────────────────────────────
DAY_TYPE_MAP = {
    "MON": "Monday",
    "TWT": "Tue-Wed-Thu",
    "FRI": "Friday",
    "SAT": "Saturday",
    "SUN": "Sunday",
}
DAY_TYPE_WEEKDAY = {"MON", "TWT", "FRI"}
DAY_TYPE_WEEKEND = {"SAT", "SUN"}

# ─── Time Periods ────────────────────────────────────────────────────────────
# As defined in NUMBAT outputs
TIME_PERIODS = {
    "Early":    ("05:00", "06:30"),
    "AM Peak":  ("06:30", "09:30"),
    "Midday":   ("09:30", "16:00"),
    "PM Peak":  ("16:00", "19:00"),
    "Evening":  ("19:00", "22:00"),
    "Late":     ("22:00", "04:59"),
}

# ─── Standard Column Renames ─────────────────────────────────────────────────
# Maps raw column names → standardised names
PERIOD_COL_MAP = {
    "Early     ": "early",
    "AM Peak   ": "am_peak",
    "Midday    ": "midday",
    "PM Peak   ": "pm_peak",
    "Evening   ": "evening",
    "Late      ": "late",
}

# ─── Random Seed ─────────────────────────────────────────────────────────────
RANDOM_SEED = 42

# ─── Logging ─────────────────────────────────────────────────────────────────
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)-30s | %(message)s"

# ─── Dashboard ───────────────────────────────────────────────────────────────
DASHBOARD_TITLE   = "METROPULSE — Urban Mobility Intelligence Platform"
DASHBOARD_FAVICON = "🚇"

# ─── Mapbox / TfL Coordinates ────────────────────────────────────────────────
# TfL Open Data — approximate centre of London for map default
MAP_DEFAULT_LAT = 51.5074
MAP_DEFAULT_LON = -0.1278
MAP_DEFAULT_ZOOM = 10

