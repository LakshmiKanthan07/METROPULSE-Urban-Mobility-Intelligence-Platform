# METROPULSE — Tableau & Power BI Integration Guide

## 1. Overview
METROPULSE exports an enterprise-grade Star Schema in CSV format (`data/bi_exports/`) specifically structured for immediate import into Microsoft Power BI, Tableau Desktop/Server, Looker, or Snowflake.

---

## 2. Star Schema Entity-Relationship Structure

```
                      ┌──────────────────────┐
                      │    dim_station       │
                      │  (nlc, asc, station, │
                      │      fare_zone)      │
                      └──────────┬───────────┘
                                 │
                                 │ 1:N
                                 ▼
┌──────────────────────┐      ┌─────────────────────────┐      ┌──────────────────────┐
│   dim_date_profile   │ 1:N  │   fact_station_demand   │ N:1  │  dim_time_interval   │
│ (year, day_type,     ├─────►│  (nlc, year, day_type,  │◄─────┤ (time_interval,      │
│  day_label, weekend) │      │  daily_entries, exits)  │      │  start_minute, period│
└──────────┬───────────┘      └─────────────────────────┘      └──────────────────────┘
           │
           │ 1:N
           ▼
┌─────────────────────────┐   N:1   ┌──────────────────────┐
│    fact_link_demand     │◄────────┤       dim_line       │
│ (link, line, dir, load, ├────────►│ (line_code,          │
│  am_peak, pm_peak)      │         │  line_name)          │
└─────────────────────────┘         └──────────────────────┘
```

---

## 3. Fact and Dimension Tables

| File Name | Role | Primary Key | Key Measures / Attributes |
|---|---|---|---|
| `fact_station_demand.csv` | Fact | `[nlc, year, day_type]` | `daily_entries`, `daily_exits`, `fare_zone` |
| `fact_link_demand.csv` | Fact | `[link, year, day_type]` | `total`, `early`, `am_peak`, `midday`, `pm_peak`, `evening`, `late` |
| `fact_service_frequency.csv` | Fact | `[link, year, day_type]` | `total`, `am_peak`, `pm_peak`, `midday` |
| `dim_station.csv` | Dimension | `nlc` | `asc`, `station`, `fare_zone` |
| `dim_line.csv` | Dimension | `line_code` | `line_name` |
| `dim_date_profile.csv` | Dimension | `[year, day_type]` | `day_type_label`, `is_weekend` |
| `dim_time_interval.csv` | Dimension | `time_interval` | `start_minute`, `period` |

---

## 4. Power BI Implementation Instructions
1. **Get Data**: Select *Folder* or *Text/CSV* and point to `data/bi_exports/`.
2. **Model View Relationships**:
   - `fact_station_demand[nlc]` $\rightarrow$ `dim_station[nlc]` (Many-to-One, Single direction)
   - `fact_station_demand[year]` & `[day_type]` $\rightarrow$ `dim_date_profile[year]` & `[day_type]`
   - `fact_link_demand[line]` $\rightarrow$ `dim_line[line_name]`
3. **Recommended DAX Measures**:
   ```dax
   Total Entries = SUM(fact_station_demand[daily_entries])
   
   Total Exits = SUM(fact_station_demand[daily_exits])
   
   AM Peak Load = SUM(fact_link_demand[am_peak])
   
   AM Peak Trains = SUM(fact_service_frequency[am_peak])
   
   AM Load Per Train = DIVIDE([AM Peak Load], [AM Peak Trains], BLANK())
   
   Net Station Inflow = [Total Entries] - [Total Exits]
   ```

---

## 5. Tableau Implementation Instructions
1. Open Tableau and select *Text file* $\rightarrow$ import `fact_station_demand.csv`.
2. In the Data Source Canvas, add `dim_station.csv` using a logical relationship on `nlc = nlc`.
3. Relate `dim_date_profile.csv` on `year = year` AND `day_type = day_type`.
4. Create a Tableau Calculated Field for **Load per Train**:
   ```tableau
   SUM([fact_link_demand].[am_peak]) / SUM([fact_service_frequency].[am_peak])
   ```

