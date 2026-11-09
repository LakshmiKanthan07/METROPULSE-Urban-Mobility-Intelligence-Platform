# 🚇 METROPULSE — Urban Mobility Intelligence Platform
### DataNova Global Data-thon 2026 | Problem Statement ID: DN-DS-01
**Title:** Urban Mobility Pattern Analysis from Transit Data  
**Focus:** London Underground Passenger Mobility Intelligence (TfL NUMBAT 2023–2025)

---

## 🌟 Executive Overview
**METROPULSE** is a full-stack, end-to-end Urban Mobility Intelligence Platform built using official Transport for London (TfL) NUMBAT datasets. It ingests 15 multi-sheet Excel workbooks across 2023, 2024, and 2025, isolates London Underground operations, standardizes 15-minute operating intervals, identifies network bottlenecks, evaluates service adequacy, predicts demand profiles using machine learning, and presents findings through an interactive multi-page command center.

---

## 🚀 Key Features & Capabilities

1. **Enterprise-Grade Reusable ETL Pipeline**:
   - Automated multi-year file discovery and dynamic sheet inspection.
   - Strict London Underground (LU) filtering across 10 Tube lines.
   - Melting 96 discrete 15-minute intervals into long-form analytics tables.
   - Dual-storage architecture: fast analytical Parquet (`data/processed/parquet/`) and CSV (`data/processed/csv/`).

2. **Advanced Transit Analytics**:
   - Station and line demand rankings.
   - Net passenger flow and directional inflow/outflow asymmetry.
   - Peak congestion detection (AM peak 07:30–08:45, PM peak 17:15–18:45).
   - Passenger Load per Train ($LPT$) congestion proxy.
   - **Service Adequacy Index (SAI)** combining demand, headway frequency, and crowding.

3. **Geospatial & Accessibility Intelligence**:
   - WGS84 and British National Grid (EPSG:27700) station projections.
   - Spatial distance decay gradient from central London (Charing Cross).
   - Nearest-neighbor station spacing and outer zone accessibility gap detection.

4. **Machine Learning & Predictive Modeling**:
   - **Leave-One-Year-Out validation** for generalized demand estimation on typical-day profiles.
   - Benchmark models: Seasonal Naive, Ridge Regression, Random Forest, Gradient Boosting, XGBoost.
   - Supervised congestion risk classification (Low, Moderate, High, Critical).
   - Unsupervised K-Means and DBSCAN station topology clustering.

5. **Network Optimization**:
   - Directed graph construction in NetworkX (nodes = stations, edges = track links).
   - Degree and Betweenness centrality computations.
   - Topological bottleneck isolation and $+25\%$ headway frequency relief simulation.

6. **Interactive Command-Center Dashboard (Streamlit)**:
   - 7 dedicated, styled, dark-navy pages with interactive Plotly visualizations.

7. **Enterprise BI Export**:
   - Star Schema fact and dimension tables for Microsoft Power BI and Tableau (`data/bi_exports/`).

---

## 🛠️ Technology Stack
- **Language**: Python 3.11 / 3.12 / 3.13
- **Data Engineering**: Pandas, NumPy, OpenPyXL, PyArrow
- **Machine Learning**: Scikit-Learn, XGBoost, LightGBM, SciPy, Statsmodels
- **Geospatial**: GeoPandas, Shapely, PyProj, Folium
- **Network Science**: NetworkX
- **Visualization**: Plotly, Matplotlib, Seaborn
- **Dashboard**: Streamlit
- **Testing**: Pytest

---

## 📂 Project Directory Structure

```
datonavathon/
├── data/
│   ├── raw/                 # 15 original TfL NUMBAT workbooks
│   ├── interim/             # Staging files
│   ├── processed/
│   │   ├── csv/             # Cleaned analytical CSV files
│   │   └── parquet/         # High-performance Parquet datasets
│   ├── external/            # Authoritative TfL station coordinates
│   └── bi_exports/          # Star-schema tables for Power BI / Tableau
├── notebooks/               # 5 Reproducible Jupyter Notebooks
├── src/
│   ├── config/              # Central settings and data dictionary
│   ├── ingestion/           # Dynamic workbook reader and inventory
│   ├── preprocessing/       # Mode filtering, standardization, cleaning
│   ├── analytics/           # Demand, congestion, service adequacy
│   ├── geospatial/          # Station mapping and spatial accessibility
│   ├── ml/                  # Feature engineering, demand & congestion models
│   ├── optimization/        # NetworkX graph and service scenarios
│   └── pipeline/            # Reusable ETL runner
├── dashboard/               # 7-page interactive Streamlit dashboard
├── reports/                 # Comprehensive analysis report and data quality HTML
├── docs/                    # Technical architecture, methodology, data dictionary
├── tests/                   # Pytest automated test suite
├── requirements.txt         # Verified dependencies
├── run.py                   # Master pipeline CLI runner
└── README.md
```

---

## ⚡ Execution Instructions

### 1. Environment Setup
```bash
pip install -r requirements.txt
```

### 2. Execute Data Pipeline Stages
Run any stage or the entire pipeline using `run.py`:

```bash
# Generate source inventory report
python run.py --stage inventory

# Execute complete ETL preprocessing & generate Parquet/CSV
python run.py --stage preprocess

# Execute mobility, congestion & service adequacy analytics
python run.py --stage analytics

# Execute machine learning models and clustering
python run.py --stage ml

# Execute geospatial accessibility modeling
python run.py --stage geospatial

# Execute network graph centrality & bottleneck optimization
python run.py --stage optimization

# Generate star-schema BI exports
python run.py --stage bi_exports

# Or execute everything end-to-end:
python run.py --stage all
```

### 3. Launch Interactive Streamlit Dashboard
```bash
streamlit run dashboard/app.py
```
Open your browser to `http://localhost:8501`.

### 4. Run Automated Test Suite
```bash
pytest tests/ -v
```

---

## 📊 Summary of Deliverables

| Deliverable | Location | Description |
|---|---|---|
| **Streamlit Dashboard** | `dashboard/app.py` | 7-page dark-themed analytics portal |
| **Clean Parquet Data** | `data/processed/parquet/` | 8 optimized analytical tables |
| **Clean CSV Data** | `data/processed/csv/` | 8 full standardized datasets |
| **BI Star Schema** | `data/bi_exports/` | Power BI & Tableau ready tables |
| **Analysis Notebooks** | `notebooks/` | 5 reproducible Jupyter notebooks (01–05) |
| **Master Report** | `reports/analysis_report.md` | Answers to all 12 analytical questions |
| **Data Quality Report**| `reports/data_quality_report.html` | Quality audit and filtering verification |
| **Technical Docs** | `docs/` | Architecture, Methodology, Data Dictionary |
| **Test Suite** | `tests/` | Unit and integration test suite |

