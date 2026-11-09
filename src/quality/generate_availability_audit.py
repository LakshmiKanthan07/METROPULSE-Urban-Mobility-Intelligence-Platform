"""
METROPULSE — Comprehensive Data Availability & Missing Data Audit
Generates:
  1. reports/missing_data_report.md
  2. reports/missing_data_report.csv
  3. reports/data_availability_matrix.csv
  4. reports/metric_dependency_report.csv
  5. reports/USER_INPUT_REQUIRED.md
"""
import sys
from pathlib import Path
import pandas as pd
import numpy as np

_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from src.config.settings import REPORTS_DIR

def run_audit():
    reports_dir = REPORTS_DIR
    reports_dir.mkdir(parents=True, exist_ok=True)

    metrics_audit = [
        # --- PASSENGER ANALYTICS ---
        {
            "metric_name": "Total Passenger Demand",
            "category": "Passenger Analytics",
            "description": "System-wide aggregate passenger volume across lines, stations, and intervals.",
            "dashboard_page": "1_Overview, 2_Demand_Analysis",
            "status": "AVAILABLE",
            "source_workbook": "All 15 NBT*.xlsx workbooks",
            "source_worksheet": "Line_Boarders, Station_Entries, Station_Exits",
            "source_columns": "total, early, am_peak, midday, pm_peak, evening, late",
            "is_derivable": True,
            "formula": "sum(passengers) across filtered dimensions",
            "external_req": "None",
            "suggested_source": "TfL NUMBAT",
            "user_input_req": "None",
            "impact_if_unavailable": "Core system visibility lost",
            "recommended_resolution": "Direct computation from tube_line_boarders and tube_station_entries",
            "data_lineage": "OBSERVED"
        },
        {
            "metric_name": "Demand by Station",
            "category": "Passenger Analytics",
            "description": "Daily and periodic entries and exits for each of the 270 London Underground stations.",
            "dashboard_page": "1_Overview, 2_Demand_Analysis, 4_Geospatial",
            "status": "AVAILABLE",
            "source_workbook": "All 15 NBT*.xlsx workbooks",
            "source_worksheet": "Station_Entries, Station_Exits",
            "source_columns": "nlc, asc, station, total, early, am_peak, midday, pm_peak, evening, late",
            "is_derivable": True,
            "formula": "groupby(asc)['daily_entries', 'daily_exits'].sum()",
            "external_req": "None",
            "suggested_source": "TfL NUMBAT",
            "user_input_req": "None",
            "impact_if_unavailable": "Station ranking and hotspot identification unavailable",
            "recommended_resolution": "Direct computation from tube_station_entries and tube_station_exits",
            "data_lineage": "OBSERVED"
        },
        {
            "metric_name": "Demand by Line",
            "category": "Passenger Analytics",
            "description": "Aggregate daily passenger boardings across the 10 Tube lines.",
            "dashboard_page": "1_Overview, 2_Demand_Analysis",
            "status": "AVAILABLE",
            "source_workbook": "All 15 NBT*.xlsx workbooks",
            "source_worksheet": "Line_Boarders",
            "source_columns": "line_code, line_name, total, passengers",
            "is_derivable": True,
            "formula": "groupby(line_name)['daily_boarders'].sum()",
            "external_req": "None",
            "suggested_source": "TfL NUMBAT",
            "user_input_req": "None",
            "impact_if_unavailable": "Line-level market share unavailable",
            "recommended_resolution": "Direct computation from tube_line_boarders",
            "data_lineage": "OBSERVED"
        },
        {
            "metric_name": "Demand by Direction",
            "category": "Passenger Analytics",
            "description": "Inbound/Outbound, Northbound/Southbound, Eastbound/Westbound passenger split.",
            "dashboard_page": "2_Demand_Analysis, 3_Congestion",
            "status": "AVAILABLE",
            "source_workbook": "All 15 NBT*.xlsx workbooks",
            "source_worksheet": "Link_Loads, Station_Boarders, Station_Alighters",
            "source_columns": "direction, total, passengers",
            "is_derivable": True,
            "formula": "groupby(['line', 'direction'])['passengers'].sum()",
            "external_req": "None",
            "suggested_source": "TfL NUMBAT",
            "user_input_req": "None",
            "impact_if_unavailable": "Directional tidal flow analysis impossible",
            "recommended_resolution": "Direct computation from tube_link_loads and station boarders",
            "data_lineage": "OBSERVED"
        },
        {
            "metric_name": "Demand by 15-Minute Interval",
            "category": "Passenger Analytics",
            "description": "Granular temporal demand curves across 96 discrete operating intervals (05:00 to 24:00+).",
            "dashboard_page": "1_Overview, 2_Demand_Analysis",
            "status": "AVAILABLE",
            "source_workbook": "All 15 NBT*.xlsx workbooks",
            "source_worksheet": "Link_Loads, Station_Entries, Station_Exits",
            "source_columns": "time_interval, start_minute, passengers",
            "is_derivable": True,
            "formula": "groupby(['time_interval', 'start_minute'])['passengers'].sum()",
            "external_req": "None",
            "suggested_source": "TfL NUMBAT",
            "user_input_req": "None",
            "impact_if_unavailable": "Peak surge analysis impossible",
            "recommended_resolution": "Melted 96 interval columns into long-form analytics table",
            "data_lineage": "OBSERVED"
        },
        {
            "metric_name": "Passenger Boardings and Alightings",
            "category": "Passenger Analytics",
            "description": "Platform-level boarding and alighting activity distinguishing train transfer from street entry.",
            "dashboard_page": "2_Demand_Analysis",
            "status": "AVAILABLE",
            "source_workbook": "All 15 NBT*.xlsx workbooks",
            "source_worksheet": "Station_Boarders, Station_Alighters",
            "source_columns": "asc, line, direction, platform, total, passengers",
            "is_derivable": True,
            "formula": "groupby(['asc', 'line'])['passengers'].sum()",
            "external_req": "None",
            "suggested_source": "TfL NUMBAT",
            "user_input_req": "None",
            "impact_if_unavailable": "Interchange transfer volume indistinguishable from street walk-in",
            "recommended_resolution": "Direct computation from tube_station_boarders and alighters",
            "data_lineage": "OBSERVED"
        },
        {
            "metric_name": "Passenger Origin-Destination Matrix",
            "category": "Passenger Analytics",
            "description": "Full end-to-end station-pair (O-D) passenger journey flows across the complete network.",
            "dashboard_page": "2_Demand_Analysis",
            "status": "PARTIALLY AVAILABLE",
            "source_workbook": "All 15 NBT*.xlsx workbooks",
            "source_worksheet": "Station_Flows (internal complex movements only)",
            "source_columns": "from_asc, to_asc, from_node, to_node, movement, passengers",
            "is_derivable": False,
            "formula": "N/A (NUMBAT Station_Flows captures interchange passages, not trip origins and final destinations)",
            "external_req": "TfL Rolling Origin & Destination Survey (RODS) or Oyster/Contactless OD matrix",
            "suggested_source": "TfL Open Data: Origin-Destination Journey Matrices",
            "user_input_req": "Approval to restrict display to Station Complex Interchanges rather than full city trips",
            "impact_if_unavailable": "Network-wide OD chord diagrams cannot show complete multi-line trips",
            "recommended_resolution": "Clearly label as 'Station Complex Movements' and note OD survey requirement",
            "data_lineage": "PARTIALLY AVAILABLE (STATION COMPLEX FLOWS ONLY)"
        },
        {
            "metric_name": "Station Entries and Exits",
            "category": "Passenger Analytics",
            "description": "Street-level fare gate tap-ins and tap-outs per station.",
            "dashboard_page": "1_Overview, 2_Demand_Analysis",
            "status": "AVAILABLE",
            "source_workbook": "All 15 NBT*.xlsx workbooks",
            "source_worksheet": "Station_Entries, Station_Exits",
            "source_columns": "asc, nlc, station, fare_zone, total, passengers",
            "is_derivable": True,
            "formula": "Direct observed sum",
            "external_req": "None",
            "suggested_source": "TfL NUMBAT",
            "user_input_req": "None",
            "impact_if_unavailable": "Entry/exit asymmetry calculations impossible",
            "recommended_resolution": "Direct computation from tube_station_entries and tube_station_exits",
            "data_lineage": "OBSERVED"
        },

        # --- SERVICE ANALYTICS ---
        {
            "metric_name": "Train Frequency",
            "category": "Service Analytics",
            "description": "Hourly number of trains operating through each track link in each direction.",
            "dashboard_page": "3_Congestion, 6_Optimization",
            "status": "AVAILABLE",
            "source_workbook": "All 15 NBT*.xlsx workbooks",
            "source_worksheet": "Link_Frequencies",
            "source_columns": "link, line, direction, total, early, am_peak, midday, pm_peak, evening, late",
            "is_derivable": True,
            "formula": "Direct observed trains per hour/period",
            "external_req": "None",
            "suggested_source": "TfL NUMBAT",
            "user_input_req": "None",
            "impact_if_unavailable": "Load per train cannot be computed",
            "recommended_resolution": "Direct computation from tube_link_frequencies",
            "data_lineage": "OBSERVED"
        },
        {
            "metric_name": "Passenger Load Per Train (LPT)",
            "category": "Service Analytics",
            "description": "Average number of passengers aboard each train traversing a track link.",
            "dashboard_page": "3_Congestion, 6_Optimization",
            "status": "DERIVABLE",
            "source_workbook": "All 15 NBT*.xlsx workbooks",
            "source_worksheet": "Link_Loads, Link_Frequencies",
            "source_columns": "Link_Loads.total, Link_Frequencies.total",
            "is_derivable": True,
            "formula": "link_load / frequency.replace(0, nan)",
            "external_req": "None",
            "suggested_source": "TfL NUMBAT",
            "user_input_req": "None",
            "impact_if_unavailable": "Crowding levels cannot be measured",
            "recommended_resolution": "Computed in src/analytics/congestion.py",
            "data_lineage": "DERIVED"
        },
        {
            "metric_name": "Actual Train Crush Capacity",
            "category": "Service Analytics",
            "description": "Physical passenger carrying capacity of train rolling stock by line (seated + standing).",
            "dashboard_page": "3_Congestion",
            "status": "UNAVAILABLE",
            "source_workbook": "None (Not present in NUMBAT workbooks)",
            "source_worksheet": "N/A",
            "source_columns": "N/A",
            "is_derivable": False,
            "formula": "N/A (Requires rolling stock fleet specs: e.g. 1992 Stock vs 2009 Stock)",
            "external_req": "TfL Rolling Stock Capacity Data Sheet",
            "suggested_source": "TfL Rolling Stock Fleet Specifications (e.g. Victoria 2009 Tube Stock: ~1,194 max crush capacity)",
            "user_input_req": "User approval of nominal rolling stock capacity parameter (e.g., 1,000 pax/train) or external specification lookup table",
            "impact_if_unavailable": "Absolute crowding % (occupancy rate) cannot be displayed; must use relative LPT and SAI",
            "recommended_resolution": "Display 'Requires External Dataset' and present relative Load-Per-Train instead of unverified % occupancy",
            "data_lineage": "REQUIRES EXTERNAL DATA"
        },
        {
            "metric_name": "Train Occupancy Percentage",
            "category": "Service Analytics",
            "description": "Passenger load divided by physical train design capacity (% full).",
            "dashboard_page": "3_Congestion",
            "status": "UNAVAILABLE",
            "source_workbook": "None",
            "source_worksheet": "N/A",
            "source_columns": "N/A",
            "is_derivable": False,
            "formula": "(load_per_train / train_capacity) * 100",
            "external_req": "Rolling stock capacity by line",
            "suggested_source": "TfL Rolling Stock Fleet Manual",
            "user_input_req": "User input on whether to use nominal capacity estimates or suppress metric",
            "impact_if_unavailable": "Absolute percentage fullness cannot be asserted without violating data integrity",
            "recommended_resolution": "Strict adherence to Data Integrity Rule: Suppress fake occupancy % and show Load-Per-Train",
            "data_lineage": "UNAVAILABLE"
        },
        {
            "metric_name": "Service Adequacy Index (SAI)",
            "category": "Service Analytics",
            "description": "Composite normalized deficit score combining normalized demand, frequency shortfall, and load per train.",
            "dashboard_page": "3_Congestion, 6_Optimization",
            "status": "DERIVABLE",
            "source_workbook": "All 15 NBT*.xlsx workbooks",
            "source_worksheet": "Link_Loads, Link_Frequencies",
            "source_columns": "Link_Loads.passengers, Link_Frequencies.frequency",
            "is_derivable": True,
            "formula": "Norm(Demand) * (1 - Norm(Frequency)) * Norm(LPT) * 100",
            "external_req": "None",
            "suggested_source": "Derived Analytical Model",
            "user_input_req": "None",
            "impact_if_unavailable": "Capacity-demand imbalances cannot be ranked",
            "recommended_resolution": "Computed in src/analytics/service_adequacy.py",
            "data_lineage": "DERIVED"
        },
        {
            "metric_name": "Real-Time Train Delays & Disruptions",
            "category": "Service Analytics",
            "description": "Real-time unplanned signal failures, track delays, and headways deviation.",
            "dashboard_page": "3_Congestion",
            "status": "NOT APPLICABLE",
            "source_workbook": "None (NUMBAT is a typical-day planning model, not real-time telemetry)",
            "source_worksheet": "N/A",
            "source_columns": "N/A",
            "is_derivable": False,
            "formula": "N/A",
            "external_req": "TfL Live Trackbot API / Unified API Line Disruptions feed",
            "suggested_source": "TfL Unified API (https://api.tfl.gov.uk/Line/Mode/tube/Status)",
            "user_input_req": "None",
            "impact_if_unavailable": "No real-time delay tracking (out of scope for static NUMBAT analysis)",
            "recommended_resolution": "Display 'Planning Model: Real-Time Delays Not Applicable' badge",
            "data_lineage": "NOT APPLICABLE TO NUMBAT"
        },

        # --- GEOSPATIAL ANALYTICS ---
        {
            "metric_name": "Station Geographic Coordinates",
            "category": "Geospatial Analytics",
            "description": "Latitude and longitude for all London Underground stations in WGS84 and EPSG:27700.",
            "dashboard_page": "4_Geospatial",
            "status": "AVAILABLE",
            "source_workbook": "data/external/lu_station_coords.csv",
            "source_worksheet": "N/A (Curated authoritative TfL Station Coordinates)",
            "source_columns": "asc, lat, lon, nlc, station",
            "is_derivable": False,
            "external_req": "Already curated and verified in data/external/",
            "suggested_source": "TfL Open Data Station Locations",
            "user_input_req": "None",
            "impact_if_unavailable": "Geographic maps cannot render",
            "recommended_resolution": "Verified and loaded in src/geospatial/station_mapping.py",
            "data_lineage": "OBSERVED (AUTHORITATIVE EXTERNAL TFL)"
        },
        {
            "metric_name": "Station-to-Station Metric Distances",
            "category": "Geospatial Analytics",
            "description": "Inter-station spacing and distance to central London (Charing Cross) in kilometers.",
            "dashboard_page": "4_Geospatial",
            "status": "DERIVABLE",
            "source_workbook": "data/external/lu_station_coords.csv",
            "source_worksheet": "N/A",
            "source_columns": "lat, lon",
            "is_derivable": True,
            "formula": "Euclidean distance in EPSG:27700 British National Grid coordinates",
            "external_req": "None",
            "suggested_source": "PyProj / Shapely",
            "user_input_req": "None",
            "impact_if_unavailable": "Accessibility spacing gaps cannot be quantified",
            "recommended_resolution": "Computed in src/geospatial/accessibility.py",
            "data_lineage": "DERIVED"
        },
        {
            "metric_name": "Official PTAL (Public Transport Accessibility Level)",
            "category": "Geospatial Analytics",
            "description": "Official London-wide PTAL index (0 to 6b) assessing multi-modal walking accessibility.",
            "dashboard_page": "4_Geospatial",
            "status": "REQUIRES EXTERNAL DATA",
            "source_workbook": "None",
            "source_worksheet": "N/A",
            "source_columns": "N/A",
            "is_derivable": False,
            "formula": "Requires comprehensive bus, tram, national rail timetables and walking network graphs",
            "external_req": "TfL WebCAT PTAL GIS Grid Layer",
            "suggested_source": "TfL Planning Information Database / WebCAT GIS Data",
            "user_input_req": "Approval to present 'Underground Inter-Station Spacing Index' as empirical proxy rather than claiming official multi-modal PTAL",
            "impact_if_unavailable": "Official multi-modal PTAL score cannot be asserted without full bus/rail network data",
            "recommended_resolution": "Show empirical 'Tube Isolation & Spacing Score' and label official PTAL as 'Requires External Dataset'",
            "data_lineage": "REQUIRES EXTERNAL DATA"
        },

        # --- MACHINE LEARNING ---
        {
            "metric_name": "Demand Prediction Targets",
            "category": "Machine Learning",
            "description": "Total daily passenger entries across station operating day profiles.",
            "dashboard_page": "5_Machine_Learning",
            "status": "AVAILABLE",
            "source_workbook": "All 15 NBT*.xlsx workbooks",
            "source_worksheet": "Station_Entries",
            "source_columns": "total",
            "is_derivable": True,
            "formula": "daily_entries = sum(passengers)",
            "external_req": "None",
            "suggested_source": "TfL NUMBAT",
            "user_input_req": "None",
            "impact_if_unavailable": "Supervised learning target missing",
            "recommended_resolution": "Built in src/ml/feature_engineering.py",
            "data_lineage": "OBSERVED"
        },
        {
            "metric_name": "Leave-One-Year-Out Model Performance",
            "category": "Machine Learning",
            "description": "Out-of-sample MAE, RMSE, and R2 evaluated on holdout operating years (2023, 2024, 2025).",
            "dashboard_page": "5_Machine_Learning",
            "status": "AVAILABLE",
            "source_workbook": "Derived from ML Model Evaluation",
            "source_worksheet": "N/A",
            "source_columns": "mae, rmse, r2",
            "is_derivable": True,
            "formula": "Standard scikit-learn regression metrics across holdout year",
            "external_req": "None",
            "suggested_source": "Trained Models (XGBoost, Random Forest, Ridge, GBM)",
            "user_input_req": "None",
            "impact_if_unavailable": "Model credibility unproven",
            "recommended_resolution": "Computed and stored in ml_demand_model_results.csv",
            "data_lineage": "PREDICTED / EVALUATED"
        },
        {
            "metric_name": "External Macro Explanatory Variables (Weather/GDP/Strikes)",
            "category": "Machine Learning",
            "description": "Rainfall, temperature, inflation, hybrid work mandates, industrial strike days.",
            "dashboard_page": "5_Machine_Learning",
            "status": "REQUIRES EXTERNAL DATA",
            "source_workbook": "None (NUMBAT represents normalized typical operational days, not calendar event dates)",
            "source_worksheet": "N/A",
            "source_columns": "N/A",
            "is_derivable": False,
            "formula": "N/A",
            "external_req": "Met Office London Weather / ONS Economic Indices",
            "suggested_source": "Met Office MIDAS / ONS Labor Market Statistics",
            "user_input_req": "Approval to restrict features to topological and profile features (year, day_type, central distance, fare zone)",
            "impact_if_unavailable": "Weather elasticity cannot be estimated directly from typical-day profiles",
            "recommended_resolution": "Document as an external data opportunity; rely on verified network topology features",
            "data_lineage": "REQUIRES EXTERNAL DATA"
        },

        # --- ROUTE OPTIMIZATION ---
        {
            "metric_name": "Maximum Signaling Headway Limits",
            "category": "Optimization",
            "description": "Maximum trains per hour physically permitted by signaling system by line (e.g. 36 tph on Victoria).",
            "dashboard_page": "6_Optimization",
            "status": "REQUIRES USER INPUT",
            "source_workbook": "None",
            "source_worksheet": "N/A",
            "source_columns": "N/A",
            "is_derivable": False,
            "formula": "Physical constraint parameter",
            "external_req": "TfL Signaling Asset Register",
            "suggested_source": "TfL Signaling Engineering Standards (CBTC / DTG / SelTrac)",
            "user_input_req": "Approval of maximum frequency cap parameter (Default recommended: 36 tph for automatic lines, 30 tph for conventional lines)",
            "impact_if_unavailable": "Optimization could hypothetically schedule an impossible number of trains (e.g. 60 tph)",
            "recommended_resolution": "Set realistic default caps (36 tph) with clear transparency note in UI",
            "data_lineage": "SIMULATED / PARAMETRIC"
        },
        {
            "metric_name": "Fleet & Depot Operational Constraints",
            "category": "Optimization",
            "description": "Available spare train sets, driver crew rosters, and depot maintenance capacity.",
            "dashboard_page": "6_Optimization",
            "status": "REQUIRES USER INPUT",
            "source_workbook": "None",
            "source_worksheet": "N/A",
            "source_columns": "N/A",
            "is_derivable": False,
            "formula": "N/A",
            "external_req": "TfL Rolling Stock Operations & Crew Rosters",
            "suggested_source": "TfL Operations Planning",
            "user_input_req": "Approval to treat +25% headway relief as an analytical 'Unconstrained Fleet Scenario'",
            "impact_if_unavailable": "Must clearly identify scenario as hypothetical decision support, not approved operational timetable",
            "recommended_resolution": "Label scenario simulation prominently as 'SIMULATED SCENARIO — UNCONSTRAINED FLEET ASSUMPTION'",
            "data_lineage": "SIMULATED"
        }
    ]

    df_matrix = pd.DataFrame(metrics_audit)

    # 1. Save data_availability_matrix.csv
    df_matrix.to_csv(reports_dir / "data_availability_matrix.csv", index=False)
    print("Saved: data_availability_matrix.csv")

    # 2. Save metric_dependency_report.csv
    dep_cols = ["metric_name", "category", "status", "source_workbook", "source_worksheet", "source_columns", "external_req", "user_input_req"]
    df_matrix[dep_cols].to_csv(reports_dir / "metric_dependency_report.csv", index=False)
    print("Saved: metric_dependency_report.csv")

    # 3. Missing Data Report CSV & MD
    missing_items = df_matrix[df_matrix["status"].isin(["UNAVAILABLE", "PARTIALLY AVAILABLE", "REQUIRES EXTERNAL DATA", "REQUIRES USER INPUT", "NOT APPLICABLE"])]
    missing_items.to_csv(reports_dir / "missing_data_report.csv", index=False)
    print("Saved: missing_data_report.csv")

    # Generate Markdown Missing Data Report
    md_missing = [
        "# METROPULSE — Data Availability & Missing Data Audit Report",
        "## Comprehensive Audit of Official TfL NUMBAT Datasets (2023–2025)",
        "",
        "### Executive Summary",
        f"A total of **{len(df_matrix)} core urban mobility metrics** were systematically audited against the 15 official TfL NUMBAT workbooks.",
        "",
        "| Availability Status | Metric Count | Percentage |",
        "|---|:---:|:---:|",
    ]
    status_counts = df_matrix["status"].value_counts()
    for st, count in status_counts.items():
        pct = (count / len(df_matrix)) * 100
        md_missing.append(f"| **{st}** | {count} | {pct:.1f}% |")

    md_missing.extend([
        "",
        "---",
        "",
        "### Detailed Audit of Missing, Partial & External-Dependent Metrics",
        "",
    ])

    for idx, row in missing_items.iterrows():
        md_missing.extend([
            f"#### {row['metric_name']} (`{row['status']}`)",
            f"- **Category**: {row['category']}",
            f"- **Description**: {row['description']}",
            f"- **Dashboard Location**: `{row['dashboard_page']}`",
            f"- **Why Missing/Partial in NUMBAT**: {row['impact_if_unavailable']}",
            f"- **Suggested Authoritative External Source**: {row['suggested_source']}",
            f"- **User Input Requirement**: {row['user_input_req']}",
            f"- **Strict Data Integrity Policy**: {row['recommended_resolution']}",
            "",
        ])

    with open(reports_dir / "missing_data_report.md", "w", encoding="utf-8") as f:
        f.write("\n".join(md_missing))
    print("Saved: missing_data_report.md")

    # 4. Generate USER_INPUT_REQUIRED.md
    md_user_input = [
        "# ⚠️ METROPULSE — User Input & Decision Approval Register",
        "## DataNova Global Data-thon 2026 | Problem Statement DN-DS-01",
        "",
        "> [!IMPORTANT]",
        "> **Strict Data Integrity Protocol**: In accordance with Section 2 of the Master Prompt, METROPULSE strictly prohibits fabricating, randomly generating, or silently substituting missing values. The following items represent values, external datasets, parameters, and analytical assumptions that require explicit user review and approval before they can be integrated into production results.",
        "",
        "---",
        "",
        "### 1. Essential Missing Information (Requiring Approval to Define Parameters)",
        "",
        "#### Item 1.1: Maximum Signaling Frequency Caps by Line",
        "- **Field / Parameter**: Maximum Permitted Trains Per Hour ($TPH_{max}$) for Optimization Scenarios.",
        "- **Why Required**: Prevents the NetworkX route optimization simulator from proposing physically impossible schedules (e.g., >40 tph).",
        "- **Where Used**: `dashboard/pages/6_Optimization.py`, `src/optimization/service_optimizer.py`.",
        "- **Impact if Unavailable**: Default safety caps are used (36 tph for automatic lines like Victoria, 30 tph for conventional lines like Bakerloo/Piccadilly).",
        "- **Expected Format & Unit**: Integer ($tph$ between 20 and 36).",
        "- **Suggested Source**: TfL Signaling Engineering Asset Register.",
        "- **Requires Approval**: **YES** — Confirm whether 36 tph (Victoria) and 30 tph (other lines) are accepted as standard engineering ceiling constraints.",
        "",
        "#### Item 1.2: Nominal Train Crush Capacity by Rolling Stock",
        "- **Field / Parameter**: Maximum passenger capacity per train ($Cap_{train}$).",
        "- **Why Required**: Calculating absolute percentage train occupancy (% fullness).",
        "- **Where Used**: `dashboard/pages/3_Congestion.py`.",
        "- **Impact if Unavailable**: Absolute % fullness is **suppressed** to avoid fabricating metrics. The system displays relative **Load-Per-Train (LPT)** and **Service Adequacy Index (SAI)** instead.",
        "- **Expected Format & Unit**: Integer passengers/train (e.g., 1,000 to 1,200).",
        "- **Suggested Source**: TfL Rolling Stock Fleet Specifications.",
        "- **Requires Approval**: **YES** — Decide whether to: (A) supply verified rolling stock capacities per line, (B) approve a standard benchmark parameter (e.g. 1,050 pax/train), or (C) keep absolute occupancy % suppressed in favor of observed LPT.",
        "",
        "---",
        "",
        "### 2. Optional Enhancements & Analytical Assumptions",
        "",
        "#### Item 2.1: Full City-Wide Origin-Destination Matrices vs Station Complex Flows",
        "- **Context**: NUMBAT `Station_Flows` captures interchange movements within complex stations (e.g. platform-to-platform transfers at Oxford Circus or Bank), but does NOT record individual journey origin-destination station pairs across the whole city.",
        "- **Assumption Requiring Approval**: Approve displaying OD chord charts as *'Station Complex Interchange Movements'* rather than full multi-leg city trips.",
        "- **Alternative**: Ingest external TfL RODS (Rolling Origin & Destination Survey).",
        "- **Requires Approval**: **YES**.",
        "",
        "#### Item 2.2: Tube Spacing Accessibility Proxy vs Official Multi-Modal PTAL",
        "- **Context**: Official London PTAL (Public Transport Accessibility Levels) scores require walking networks, bus route schedules, and national rail feeds outside NUMBAT.",
        "- **Assumption Requiring Approval**: Approve displaying the computed *'Underground Station Spacing & Distance Decay Index'* as an empirical Tube accessibility measure, while clearly indicating that official multi-modal PTAL requires external GIS layers.",
        "- **Requires Approval**: **YES**.",
        "",
        "---",
        "",
        "### 3. External Datasets to Potentially Obtain (Future Roadmap)",
        "",
        "| External Dataset | Authority / Source | Analytical Capability Unlocked | Priority |",
        "|---|---|---|:---:|",
        "| **TfL Rolling Stock Fleet Capacity Register** | TfL Engineering | Converts Load-Per-Train into exact % vehicle occupancy | High |",
        "| **TfL Live Trackbot / Unified API Disruptions** | TfL Open Data | Overlays historical delays and signal incidents onto NUMBAT planned profiles | Medium |",
        "| **TfL WebCAT Multi-Modal PTAL GIS Shapefiles** | TfL Planning | Adds full London-wide multi-modal accessibility layers (bus + tram + rail) | Medium |",
        "| **Met Office London Climate & Weather Data** | Met Office MIDAS | Enables weather sensitivity elasticity regression in ML | Low |",
        "",
        "---",
        "",
        "### 4. Dashboard Features Currently Handled via Graceful Fallback States",
        "",
        "In strict adherence to the **Data Integrity Principle**, the following UI states are actively rendered where source data is incomplete:",
        "1. **Train Occupancy %**: Displays `[REQUIRES EXTERNAL CAPACITY DATA]` badge instead of a fabricated percentage.",
        "2. **Real-Time Delays**: Displays `[PLANNING MODEL — REAL-TIME DELAYS NOT APPLICABLE]` badge.",
        "3. **Multi-Modal Trips**: Labeled as `[STATION COMPLEX TRANSFERS ONLY — OD SURVEY REQUIRED FOR FULL TRIPS]`.",
        "4. **Simulation Scenarios**: Prominently watermarked as `[SIMULATED SCENARIO — UNCONSTRAINED FLEET ASSUMPTION]`.",
        "",
        "---",
        "*Report generated automatically by METROPULSE Data Quality & Audit Engine.*"
    ]

    with open(reports_dir / "USER_INPUT_REQUIRED.md", "w", encoding="utf-8") as f:
        f.write("\n".join(md_user_input))
    print("Saved: USER_INPUT_REQUIRED.md")

if __name__ == "__main__":
    run_audit()

