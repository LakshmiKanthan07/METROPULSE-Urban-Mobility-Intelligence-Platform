# METROPULSE — Data Dictionary

## 1. Overview
The METROPULSE platform processes 15 multi-sheet Excel workbooks from Transport for London (TfL) Network Usage Model Based Analysis Tool (NUMBAT), covering 2023, 2024, and 2025 across five representative day types: Monday (`MON`), Tuesday–Thursday (`TWT`), Friday (`FRI`), Saturday (`SAT`), and Sunday (`SUN`).

All processed tables are filtered strictly to the **London Underground (LU)** network and stored in Parquet (`data/processed/parquet/`) and CSV (`data/processed/csv/`).

---

## 2. Table Specifications

### 2.1 `tube_link_loads`
- **Description:** Passenger link load volumes traveling between adjacent London Underground stations across a representative 24-hour service day.
- **Source Sheet:** `Link_Loads`
- **Granularity:** Link × Year × Day Type × 15-Minute Interval
- **Columns:**
  - `link` (string): Unique link key, formatted as `[From_ASC]_[Line]_[Dir]>[To_ASC]_[Line]_[Dir]@[Line]`
  - `line` (string): Underground Line name (e.g., Central, Victoria, Jubilee)
  - `line_code` (string): Standard 3-letter code (`BAK`, `CEN`, `DIS`, `HAM`, `JUB`, `MET`, `NOR`, `PIC`, `VIC`, `WAC`)
  - `direction` (string): Direction of travel (`NB`, `SB`, `EB`, `WB`)
  - `order` (integer): Sequential station order along the line branch
  - `from_nlc` (integer): Origin station National Location Code
  - `from_asc` (string): Origin Alpha Station Code (e.g., `OXCu`)
  - `from_station` (string): Origin station display name
  - `to_nlc` (integer): Destination station National Location Code
  - `to_asc` (string): Destination Alpha Station Code
  - `to_station` (string): Destination station display name
  - `total` (float): Aggregate modeled passenger count across entire day
  - `early`, `am_peak`, `midday`, `pm_peak`, `evening`, `late` (float): Period passenger sub-totals
  - `time_interval` (string): 15-minute time window in `HHMM-HHMM` format (e.g., `0730-0745`)
  - `passengers` (float): Modeled passenger count in specific 15-minute interval
  - `start_minute` (integer): Minutes elapsed from midnight (e.g., 450 for 07:30)
  - `period` (string): Canonical time-of-day category
  - `year` (integer): Dataset edition (`2023`, `2024`, `2025`)
  - `day_type` (string): Day type identifier (`MON`, `TWT`, `FRI`, `SAT`, `SUN`)
  - `day_type_label` (string): Human-readable day label

### 2.2 `tube_link_frequencies`
- **Description:** Scheduled train counts operating on each track link section.
- **Source Sheet:** `Link_Frequencies`
- **Granularity:** Link × Year × Day Type × 15-Minute Interval
- **Key Columns:** Identical schema to `tube_link_loads`, where `passengers` represents scheduled train frequency.

### 2.3 `tube_line_boarders`
- **Description:** Cumulative boardings per London Underground line across time windows.
- **Source Sheet:** `Line_Boarders`
- **Granularity:** Line Code × Year × Day Type × 15-Minute Interval
- **Columns:**
  - `mode` (string): Always `LU`
  - `line_code` (string): 3-letter line identifier
  - `line_name` (string): Full line title
  - `total` (float): Daily total boardings
  - `early` to `late` (float): Period sub-totals
  - `time_interval`, `passengers`, `start_minute`, `period`, `year`, `day_type`

### 2.4 `tube_station_entries` & `tube_station_exits`
- **Description:** Gate tap-in (entries) and tap-out (exits) volumes per station.
- **Source Sheets:** `Station_Entries`, `Station_Exits`
- **Granularity:** Station NLC × Year × Day Type × 15-Minute Interval
- **Columns:**
  - `nlc` (integer): National Location Code
  - `asc` (string): Alpha Station Code ending in `u`
  - `station` (string): Official station name
  - `fare_zone` (string): TfL fare zone (e.g., `1`, `2`, `1/2`, `3`)
  - `total` (float): Total daily entries or exits
  - `early` to `late` (float): Period sub-totals
  - `time_interval`, `passengers`, `start_minute`, `period`, `year`, `day_type`

### 2.5 `tube_station_boarders` & `tube_station_alighters`
- **Description:** Platform-level boardings and alightings per station, line, and direction.
- **Source Sheets:** `Station_Boarders`, `Station_Alighters`
- **Granularity:** Platform ID × Year × Day Type × 15-Minute Interval

### 2.6 `tube_station_flows`
- **Description:** Internal pedestrian interchange movements between lines within complex hub stations.
- **Source Sheet:** `Station_Flows`
- **Granularity:** Movement ID × Year × Day Type × 15-Minute Interval
- **Columns:**
  - `id` (string): Movement identifier
  - `complex_nlc` (integer): Interchange hub NLC
  - `from_station`, `from_node`, `to_station`, `to_node`, `movement`, `total`, `passengers`

---

## 3. Analytical & Derived Tables
- `congestion_link_congestion`: Links evaluated for AM/PM load-per-train (`pax_per_train_am_peak`), congestion class (`Low`, `Moderate`, `High`, `Critical`), and normalized congestion score (0–100).
- `service_adequacy`: Composite metric combining passenger load, train frequency, and demand scale.
- `ml_station_clusters`: Station unsupervised clusters with semantic taxonomy.
- `network_centrality`: Graph-theoretic Degree, Betweenness, and Closeness centralities.
- `network_bottlenecks`: High-load, low-frequency network choke points.
- `optimization_scenarios`: Comparative baseline vs. +25% frequency headroom scenarios.

