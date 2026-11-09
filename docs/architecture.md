# METROPULSE — System Architecture

```mermaid
flowchart TD
    subgraph S1["Stage 0: Ingestion & Inventory"]
        R["15 NUMBAT Excel Workbooks (2023-2025)"] --> INV["Inventory Engine (inventory.py)"]
        INV --> INVC["source_inventory.csv"]
    end

    subgraph S2["Stage 1 & 2: ETL & London Underground Filtering"]
        R --> EX["Workbook Reader (workbook_reader.py)"]
        EX --> MF["Mode Filter (LU Isolation)\n- Line Codes (BAK, CEN, DIS, etc.)\n- Station ASC 'u' Suffix\n- Mode == 'LU'"]
        MF --> STD["Standardization & Reshaping (standardization.py)\n- Melt 96x 15-min Intervals\n- Standardize Directions & Periods"]
        STD --> VAL["Validation & Quality Assurance (validation.py)"]
    end

    subgraph S3["Stage 3: High-Performance Storage"]
        VAL --> PQ["data/processed/parquet/ (8 Datasets)"]
        VAL --> CSV["data/processed/csv/ (8 Datasets)"]
    end

    subgraph S4["Stage 4: Analytics, Geospatial & ML Engines"]
        PQ --> DEM["Demand Analysis (demand_analysis.py)"]
        PQ --> CONG["Congestion & Load/Train (congestion.py)"]
        PQ --> ADEQ["Service Adequacy Index (service_adequacy.py)"]
        PQ --> GEO["Geospatial & Accessibility (spatial_analysis.py)"]
        PQ --> ML["Machine Learning Pipeline\n- Leave-One-Year-Out Demand Models\n- Congestion Classifier (GBM)\n- Station Clustering (K-Means)"]
        PQ --> OPT["NetworkX Graph & Optimizer\n- Betweenness Centrality\n- Bottleneck Detection\n- Headway Scenarios (+25%)"]
    end

    subgraph S5["Stage 5: Presentation & BI Delivery"]
        DEM & CONG & ADEQ & GEO & ML & OPT --> BI["data/bi_exports/ (Star Schema for Tableau & Power BI)"]
        DEM & CONG & ADEQ & GEO & ML & OPT --> ST["METROPULSE Streamlit Dashboard (7 Interactive Pages)"]
        DEM & CONG & ADEQ & GEO & ML & OPT --> NB["Jupyter Notebooks (01 to 05)"]
        DEM & CONG & ADEQ & GEO & ML & OPT --> REP["Comprehensive Analysis Reports & Slides"]
    end
```

## Directory Hierarchy & Modules
- `src/config/`: System settings, line definitions, period maps, and data dictionary.
- `src/ingestion/`: Multi-workbook dynamic discovery, sheet inspection, and automated inventory.
- `src/preprocessing/`: London Underground filtering, wide-to-long interval melting, direction standardization, and validation checks.
- `src/analytics/`: System demand rankings, inflow/outflow asymmetry, load-per-train computation, and Service Adequacy Index.
- `src/geospatial/`: BNG (EPSG:27700) metric projection, distance to central London, and spatial coverage gap detection.
- `src/ml/`: Feature matrix construction, leave-one-year-out cross-validation, LightGBM/Random Forest regression, and K-Means clustering.
- `src/optimization/`: Directed graph construction, betweenness centrality, bottleneck isolation, and +25% headway relief modeling.
- `dashboard/`: Multi-page command-center Streamlit web application.
- `data/bi_exports/`: Star schema dimension and fact tables for enterprise BI software.

