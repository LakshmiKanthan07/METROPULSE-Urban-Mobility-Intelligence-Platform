# 🚇 METROPULSE — Urban Mobility Intelligence Platform
### DataNova Global Data-thon 2026 | Problem Statement Track: DN-DS-01
**Title:** Urban Mobility Pattern Analysis from Transit Data  
**Focus:** London Underground Passenger Mobility, Congestion, and Service Adequacy Intelligence (TfL NUMBAT 2023–2025)

[![Python 3.11+](https://img.shields.io/badge/Python-3.11%20%7C%203.12%20%7C%203.13-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit App](https://img.shields.io/badge/Streamlit-Command%20Center%20Live-FF4B4B?logo=streamlit&logoColor=white)](http://localhost:8501)
[![Tests Passing](https://img.shields.io/badge/Pytest-18%20Passed%20(100%25)-10b981?logo=pytest&logoColor=white)](tests/)
[![TfL NUMBAT](https://img.shields.io/badge/Data-TfL%20NUMBAT%20(2023--2025)-0019A8?logo=transportforlondon&logoColor=white)](https://tfl.gov.uk)
[![Parquet Storage](https://img.shields.io/badge/Storage-Parquet%20%2B%20Star%20Schema-3b82f6)](data/bi_exports/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

---

## 🌟 1. Executive Summary

**METROPULSE** is an enterprise-grade, end-to-end Urban Mobility Intelligence Platform engineered to ingest, process, model, and optimize London Underground operations. Operating strictly upon official Transport for London (TfL) NUMBAT (Network Usage Model Based Analysis Tool) datasets spanning **2023, 2024, and 2025** across all five representative operating profiles (**MON, TWT, FRI, SAT, SUN**), METROPULSE transforms over **168,000 raw source rows** into **9.38 million standardized records** stored in high-performance dual Parquet/CSV analytical layers.

The platform addresses the post-pandemic evolution of public transport demand, isolates high-risk track bottlenecks, evaluates capacity imbalances via a composite **Service Adequacy Index (SAI)**, deploys **Leave-One-Year-Out predictive machine learning**, simulates graph-based service frequency optimizations, and presents operational intelligence through an interactive 7-page dark-themed Streamlit command center and star-schema exports for Microsoft Power BI and Tableau.

---

## 🏛️ 2. System Architecture & End-to-End Pipeline

METROPULSE implements a modular, decoupled data and machine learning lifecycle:

```
                                      METROPULSE ARCHITECTURE
 ┌─────────────────────────────────────────────────────────────────────────────────────────────┐
 │ 1. INGESTION & DISCOVERY                                                                    │
 │    • 15 TfL NUMBAT Excel Workbooks (2023–2025) across 5 Day Types (MON, TWT, FRI, SAT, SUN) │
 │    • Dynamic casing discovery, schema auditing & source inventory (168,330 raw rows)        │
 └──────────────────────────────────────────────┬──────────────────────────────────────────────┘
                                                │
                                                ▼
 ┌─────────────────────────────────────────────────────────────────────────────────────────────┐
 │ 2. DATA ENGINEERING & LU MODE FILTERING (ETL Stage 1 to 3)                                  │
 │    • Deterministic London Underground (LU) isolation across 10 lines (BAK, CEN, DIS, etc.) │
 │    • Station ASC 'u' suffix filtering (270 stations; eliminates railway/tram contamination) │
 │    • 96 discrete 15-minute interval melting & canonical column standardization              │
 │    • Dual Storage: 8 Parquet files (PyArrow fast I/O) + 8 CSV files (9.38M records)         │
 └──────────────────────────────────────────────┬──────────────────────────────────────────────┘
                                                │
                                                ▼
 ┌─────────────────────────────────────────────────────────────────────────────────────────────┐
 │ 3. ANALYTICAL ENGINES & GEOSPATIAL INTELLIGENCE                                             │
 │    • Station & Line Demand Rankings | Directional Tap-In vs. Tap-Out Asymmetry Ratios       │
 │    • Load-Per-Train (LPT) Congestion Metrics | Peak Window Identification (AM/PM Spikes)    │
 │    • Service Adequacy Index (SAI) formulation combining Demand, Frequency, and Vehicle Load │
 │    • EPSG:27700 British National Grid metric spacing & Distance Decay from Central London   │
 └──────────────────────┬───────────────────────────────────────────────┬──────────────────────┘
                        │                                               │
                        ▼                                               ▼
 ┌──────────────────────────────────────────────┐ ┌────────────────────────────────────────────┐
 │ 4. MACHINE LEARNING ENGINE                   │ │ 5. NETWORK GRAPH OPTIMIZATION              │
 │    • Leave-One-Year-Out Validation (No Leak) │ │    • NetworkX Directed Graph (270N, 625E)  │
 │    • Demand: XGBoost (R²=0.988, MAE=961 pax) │ │    • Betweenness & Degree Centrality       │
 │    • Congestion Classifier (99.0% CV Acc)    │ │    • Topological Bottleneck Isolation      │
 │    • Unsupervised K-Means & DBSCAN Clusters  │ │    • +25% Frequency Relief Simulation      │
 └──────────────────────┬───────────────────────┘ └─────────────────────┬──────────────────────┘
                        │                                               │
                        └───────────────────────┬───────────────────────┘
                                                │
                                                ▼
 ┌─────────────────────────────────────────────────────────────────────────────────────────────┐
 │ 6. PRESENTATION, VISUALIZATION & BI EXPORTS                                                 │
 │    • 7-Page Interactive Streamlit Command Center (Dark Navy Theme: #0a0f1e)                 │
 │    • Star Schema Fact & Dimension Tables for Power BI and Tableau (data/bi_exports/)        │
 │    • 5 Reproducible Jupyter Notebooks (01 to 05) with Markdown narratives                   │
 │    • 14-Slide Widescreen (16:9) Executive Presentation Deck (reports/metropulse_...)        │
 │    • Standalone Data Quality HTML Report + 4 Audit CSVs                                     │
 └─────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 🔍 3. Key Analytical Findings (Direct Answers to Problem Statement)

All insights are derived strictly from the official NUMBAT data without synthetic approximations:

| Question / Dimension | Quantitative Finding & Operational Insight |
|---|---|
| **Q1: Top Stations** | **King's Cross St. Pancras (`KGXu`)** leads the network with **>240,000 daily entries and exits** on typical weekdays, followed by **Victoria (`VICu`)** (215k), **Waterloo (`WLOu`)** (195k), and **Oxford Circus (`OXCu`)** (188k). |
| **Q2: Top Lines** | **Northern line** carries the highest passenger volume with **>788,000 daily boarders**, followed by the **District line** (614k) and **Central line** (598k). The **Victoria line** exhibits the highest passenger density per route mile. |
| **Q3: Congestion Windows** | **AM Peak**: Intensely concentrated between **07:30 and 08:45**, peaking at **>140,000 boarders / 15-minute interval**. **PM Peak**: Distributed between **17:15 and 18:45**. Off-peak midday plateau stabilizes at ~60,000 boarders / 15-min. |
| **Q4: Critical Track Links** | Highest segment loads occur on **Victoria line Southbound** (Highbury & Islington $\rightarrow$ King's Cross $\rightarrow$ Euston) and **Central line Westbound** (Liverpool Street $\rightarrow$ Bank $\rightarrow$ Holborn), exceeding **55,000 pax/hr**. |
| **Q5: Service Adequacy** | While Zone 1 deep tunnels operate at 30–36 trains per hour (tph), vehicle crowding routinely exceeds **800 passengers per train**. Peripheral branches (e.g., Hainault Loop, Chesham) operate at only 4–8 tph, creating localized adequacy deficits. |
| **Q6: Route Imbalances** | Evaluated via **Service Adequacy Index (SAI)**: Central line core, Northern line Camden Town confluence, and Jubilee line (Canada Water $\rightarrow$ Canary Wharf) show highest capacity-demand stress. |
| **Q7: Flow Asymmetry** | **Residential Origins** (Brixton, Tooting, Finsbury Park, Walthamstow Central) show morning **entry-to-exit ratios > 4.5:1**. **Commercial Hubs** (Bank, Canary Wharf, Holborn) show morning **exit-to-entry ratios > 5.2:1**. |
| **Q8: Weekday vs Weekend** | Weekdays follow a **bimodal commuter curve**; weekends follow a **unimodal afternoon curve (13:00–16:30)**. Saturday daily volume is **68%** of a typical weekday; Sunday is **52%**, with traffic shifting to West End retail and leisure centers. |
| **Q9: Multi-Year Trends** | **2023 $\rightarrow$ 2024**: Network boardings surged by **+6.2%** as hybrid schedules consolidated around midweek (TWT). **2024 $\rightarrow$ 2025**: Growth stabilized at **+2.4%**. Friday PM peaks occur ~45 minutes earlier than Monday–Thursday. |
| **Q10: Targeted Headways** | Priority frequency increases (+2 to +4 tph) recommended for the Central line inner corridor (07:45–08:45) and Northern line Bank branch signaling optimization. |
| **Q11: Accessibility Gaps** | Outer terminal stations (Chesham, Amersham, Epping) have inter-station metric spacing exceeding **4.2 km**, heavily reliant on feeder buses. South London remains underserved by deep tube lines. |
| **Q12: Data-Driven Policies** | 1) Dynamic turnstile pacing at King's Cross & Victoria during AM peaks; 2) Central line short-turn trains reversing at White City; 3) Active passenger diversion to parallel Elizabeth line corridors. |

---

## 🤖 4. Machine Learning & Predictive Modeling

To prevent **temporal data leakage** inherent in representative profile datasets (where random train-test splitting shuffles identical operating schedules across sets), models were evaluated using **Leave-One-Year-Out cross-validation** across holdout years (2023, 2024, 2025).

### Model Performance Benchmark

| Model Architecture | Cross-Validation Strategy | Out-of-Sample MAE | Out-of-Sample RMSE | Holdout $R^2$ Score | Status |
|---|---|:---:|:---:|:---:|:---:|
| **XGBoost Regressor** | Leave-One-Year-Out (2025 Test) | **961 pax** | **2,033 pax** | **0.988** | 🏆 **Best Model** |
| **Random Forest Regressor** | Leave-One-Year-Out (2025 Test) | 1,031 pax | 2,288 pax | 0.985 | Strong Baseline |
| **Gradient Boosting (GBM)** | Leave-One-Year-Out (2025 Test) | 1,070 pax | 2,309 pax | 0.984 | Highly Robust |
| **Ridge Regression** | Leave-One-Year-Out (2025 Test) | 2,213 pax | 4,611 pax | 0.937 | Linear Benchmark |

### Classification & Unsupervised Clustering
- **Congestion Classifier**: Predicts operational crowding tiers (`Low`, `Moderate`, `High`, `Critical`) using independent link loads and train frequencies. Achieved **99.0% ± 0.2% 5-fold CV accuracy** (GBM).
- **Station Clustering (K-Means & DBSCAN)**: Identifies 3 distinct functional clusters ($k=3$, silhouette score $0.434$):
  1. *Major Interchange Gateways* (High volume, balanced all-day flows).
  2. *Suburban Residential Feeders* (Morning tap-in spikes, evening return flow).
  3. *Central Commercial Employment Hubs* (Extreme morning tap-out spikes).

---

## 🗺️ 5. Network Optimization & Service Scenarios

Constructed a directed multigraph $G = (V, E)$ in NetworkX with **270 station nodes** and **625 directed track links**.

```
Graph Metric                        Value
─────────────────────────────────────────────
Total Stations (Nodes)              270
Track Segments (Directed Edges)     625
Average In/Out Degree               2.31
Network Graph Diameter              34 stops
Top Betweenness Station             King's Cross St. Pancras (0.248)
```

### Headway Frequency Simulation (+25% Scenario)
- **Bottlenecks Detected**: 104 track segments exceed the critical crowding threshold of >700 passengers/train during the AM peak.
- **Relief Scenario**: Simulating a +25% frequency injection on critical bottlenecks successfully reduces maximum vehicle crowding from **842 pax/train down to 673 pax/train**, mitigating crush conditions on 100% of tested links.

---

## 📊 6. Star Schema BI Exports (Power BI & Tableau)

Seven pre-built fact and dimension tables are exported in [`data/bi_exports/`](data/bi_exports/) for seamless drag-and-drop analysis:

```
                            STAR SCHEMA ARCHITECTURE
                             ┌───────────────────┐
                             │    dim_station    │
                             │ (270 Tube Nodes)  │
                             └─────────┬─────────┘
                                       │ 1:N
 ┌──────────────────────┐    ┌─────────▼─────────┐    ┌──────────────────────┐
 │   dim_date_profile   │1:N │fact_station_demand│ N:1│  dim_time_interval   │
 │(15 Operating Profiles├───►│ (4,050 Records)   │◄───┤ (96 15-Min Windows)  │
 └──────────┬───────────┘    └───────────────────┘    └──────────┬───────────┘
            │ 1:N                                                │ 1:N
            │                ┌───────────────────┐               │
            ├───────────────►│ fact_link_demand  │◄──────────────┤
            │                │ (10,955 Records)  │               │
            │                └─────────▲─────────┘               │
            │                          │ N:1                     │
            │                ┌─────────┴─────────┐               │
            │                │     dim_line      │               │
            │                │(10 LU Line Codes) │               │
            │                └─────────┬─────────┘               │
            │                          │ N:1                     │
            │                ┌─────────▼─────────┐               │
            └───────────────►│fact_service_freq  │◄──────────────┘
                             │ (10,955 Records)  │
                             └───────────────────┘
```

See the [Power BI & Tableau Integration Guide](docs/tableau_powerbi_guide.md) for DAX formulas and relationship definitions.

---

## 🖥️ 7. Interactive Streamlit Command Center & Component Architecture

The interactive dashboard is organized into **8 specialized intelligence modules** built on a custom enterprise design system (`#080D17` Bloomberg / Linear dark aesthetic):

```
dashboard/
├── app.py                      # Main Command Center Portal & Telemetry Hub
├── components/                 # Reusable Enterprise UI Component Library
│   ├── theme.py                # Design tokens, CSS injection, dark palettes & badge styles
│   ├── header.py               # Navigation breadcrumb, active filters & timestamp bar
│   ├── sidebar.py              # Platform identity, integrity guard & network telemetry
│   ├── metric_card.py          # Zero-fabrication KPI card with lineage pills & graceful missing states
│   ├── section_header.py       # Standardized section headings with status badges
│   ├── chart_container.py      # Plotly wrapper with card background & analytical takeaways
│   ├── filter_bar.py           # Faceted multi-select filters without recomputation lag
│   ├── data_table.py           # Formatted tabular view with null markers (—) & CSV export
│   ├── empty_state.py          # Graceful UI placeholder for missing/filtered data
│   └── data_loader.py          # High-performance PyArrow Parquet cache loader
└── pages/
    ├── 1_Overview.py           # Network KPIs, 15-Min System Curves, Line Shares & YoY Trends
    ├── 2_Demand_Analysis.py    # Station Rankings, Inflow/Outflow Asymmetry Ratios, Day-Type Profiles
    ├── 3_Congestion.py         # Track Bottlenecks, Load-Per-Train Metrics & Service Adequacy Index
    ├── 4_Geospatial.py         # Mapbox Dark Bubble Maps, Fare Zone Decays & Accessibility Deficits
    ├── 5_Machine_Learning.py   # Leave-One-Year-Out Model Benchmarks & Station Topology Clustering
    ├── 6_Optimization.py       # Graph Centrality Analysis, Bottleneck Detection & +25% Scenario Simulator
    ├── 7_Data_Explorer.py      # Multi-Dataset Live Query Browser, Regex Filters & CSV Downloader
    └── 8_Data_Availability.py  # 22-Metric Availability Matrix, Missing Data Audit & Report Downloads
```

---

## 🛡️ 8. Data Integrity & Zero-Fabrication Protocol

METROPULSE strictly enforces the **Zero-Fabrication Data Integrity Principle**:
- **Zero Synthetic Substitution**: Missing indicators (e.g. physical vehicle crush capacity, real-time signal delays, multi-modal PTAL) are never fabricated with arbitrary averages or fake numbers.
- **Traceable Lineage Badges**: Every single metric, KPI card, and chart carries an explicit lineage pill:
  - `● OBSERVED`: Extracted directly from TfL NUMBAT Excel workbooks.
  - `◆ DERIVED`: Formally calculated using transparent transit mathematical equations.
  - `▲ PREDICTED`: Produced by machine learning models evaluated on out-of-sample holdout years.
  - `◈ SIMULATED`: Explicitly watermarked decision-support scenario simulations.
  - `✕ DATA NOT PROVIDED`: Graceful fallback state detailing required external datasets.
- **Audit Reports Available**:
  - [`reports/data_availability_matrix.csv`](reports/data_availability_matrix.csv): 22-metric availability audit across all TfL workbooks.
  - [`reports/missing_data_report.md`](reports/missing_data_report.md): In-depth gap analysis and fallback justifications.
  - [`reports/USER_INPUT_REQUIRED.md`](reports/USER_INPUT_REQUIRED.md): Catalog of operational parameters, external datasets, and fallback states.

To run the dashboard locally:
```bash
streamlit run dashboard/app.py
```
*Access in browser at: `http://localhost:8501`*

---

## 📁 8. Project Directory Structure

```
datonavathon/
├── .gitignore                           # Excludes heavy raw workbooks & multi-GB processed tables
├── README.md                            # Master project documentation
├── requirements.txt                     # Pinned project dependencies
├── run.py                               # Master CLI pipeline runner
├── conftest.py                          # Pytest path resolver
├── dashboard/                           # 7-page interactive Streamlit command center
│   ├── app.py                           # Landing dashboard
│   ├── components/
│   │   └── data_loader.py               # Cached Parquet reader & styling helpers
│   └── pages/                           # 7 modular intelligence pages
├── data/
│   ├── raw/                             # 15 original TfL NUMBAT Excel workbooks (preserved)
│   ├── external/                        # Station coordinates (WGS84 & EPSG:27700)
│   ├── processed/
│   │   ├── csv/                         # 8 canonical datasets + ML & analytical tables
│   │   └── parquet/                     # 8 high-performance PyArrow datasets
│   └── bi_exports/                      # Star schema tables for Power BI / Tableau
├── docs/                                # Technical engineering documentation
│   ├── architecture.md                  # System design & pipeline stages
│   ├── data_dictionary.md               # Variable definitions & canonical schemas
│   ├── methodology.md                   # Mathematical formulas (LPT, SAI, Leave-One-Year-Out)
│   ├── tableau_powerbi_guide.md         # BI connection & DAX documentation
│   └── limitations.md                   # Known constraints & analytical edge cases
├── models/                              # Serialized scikit-learn & XGBoost model artifacts (.pkl)
├── notebooks/                           # 5 Reproducible Jupyter Notebooks (01 to 05)
├── reports/                             # Executive deliverables
│   ├── analysis_report.md               # Comprehensive answers to all 12 master questions
│   ├── data_quality_report.html         # Styled HTML data audit report
│   ├── metropulse_presentation.pptx     # 14-slide widescreen (16:9) presentation deck
│   ├── figures/                         # High-resolution (300 DPI) publication charts
│   └── data_quality/                    # 4 CSV audit reports (summary, missing, dupes, schema)
└── tests/                               # Automated Pytest suite (18 unit & integration tests)
    ├── test_pipeline.py                 # Ingestion & LU filtering tests
    ├── test_analytics.py                # LPT, congestion bins & SAI bound tests
    ├── test_geospatial.py               # Bounding box & distance decay tests
    └── test_ml.py                       # Leakage detection & R² validation tests
```

---

## ⚡ 9. Step-by-Step Installation & Execution

### 1. Environment Setup
```bash
# Clone the repository
git clone https://github.com/LakshmiKanthan07/METROPULSE-Urban-Mobility-Intelligence-Platform.git
cd METROPULSE-Urban-Mobility-Intelligence-Platform

# Create and activate virtual environment
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Execute End-to-End Pipeline
Run any individual stage or the entire system end-to-end:
```bash
# Execute complete pipeline (Stages 0 through 9)
python run.py --stage all

# Or run individual stages:
python run.py --stage inventory       # Audits raw source workbooks
python run.py --stage preprocess      # Filters LU and generates Parquet/CSV
python run.py --stage analytics       # Computes demand, congestion & SAI
python run.py --stage ml              # Trains Leave-One-Year-Out models
python run.py --stage geospatial      # Computes coordinate projections
python run.py --stage optimization    # Builds graph & evaluates bottlenecks
python run.py --stage bi_exports      # Generates Star Schema tables
python run.py --stage quality_reports # Generates 4 data audit CSVs
```

### 3. Run Automated Tests
```bash
pytest tests/ -v
```

### 4. Launch Interactive Command Center
```bash
streamlit run dashboard/app.py
```

---

## 🛡️ 10. Data Quality & Audit Results

Validation gates are executed at every transformation step. Output summary:
- **Raw Workbooks Audited**: 15 Excel workbooks across 3 complete years.
- **Raw Rows Ingested**: 168,330 rows.
- **Core Field Nulls**: **0.00%** missing values across primary keys (`link`, `asc`, `nlc`, `line_code`, `time_interval`).
- **Negative Passenger Counts**: **0 detected** (all negative sensor artifacts clipped to 0.0).
- **Duplicate Records**: **0 duplicates** across Link Loads, Frequencies, Line Boarders, Station Entries/Exits, Boarders, and Alighters using domain composite keys.
- **Cross-Year Schema Consistency**: 100% harmonized across 2023, 2024, and 2025.

Audit reports available in [`reports/data_quality/`](reports/data_quality/) and [`reports/data_quality_report.html`](reports/data_quality_report.html).

---

## 👥 Authors & Hackathon Attribution

- **Lead Developer & Data Scientist**: Lakshmi Kanthan ([@LakshmiKanthan07](https://github.com/LakshmiKanthan07))
- **Hackathon**: DataNova Global Data-thon 2026
- **Problem Statement ID**: `DN-DS-01` (Urban Mobility Pattern Analysis from Transit Data)
- **Source Data**: Transport for London (TfL) Network Usage Model Based Analysis Tool (NUMBAT) 2023–2025.
- **License**: MIT Open Source License.
