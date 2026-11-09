# METROPULSE — Analytical & Scientific Methodology

## 1. Data Characterization & Context
The TfL NUMBAT (Network Usage Model Based Analysis Tool) system synthesizes automated fare collection (Oyster and contactless smartcard transactions), manual passenger surveys, and automated passenger counters into modeled **typical operating days** for designated year editions (2023, 2024, 2025) across five day classifications (`MON`, `TWT`, `FRI`, `SAT`, `SUN`).

### Methodological Rule: Non-Continuous Profiles
NUMBAT data points do **not** represent a continuous chronological time series of calendar dates. Each year/day combination is a normalized representative profile of that specific day-type. Therefore, traditional chronological time-series forecasting (e.g., standard ARIMA or random split lag regression) would create severe data leakage. METROPULSE utilizes **Leave-One-Year-Out validation** and profile-based estimation.

---

## 2. London Underground (LU) Filtering Rules
NUMBAT workbooks cover multi-modal TfL networks (LU, LO, DLR, EZL, TRM). METROPULSE isolates London Underground records using multi-tiered criteria:
1. **Explicit Mode Matching**: In `Line_Boarders`, `Station_Boarders`, and `Station_Alighters`, retain records where `Mode == 'LU'`.
2. **Station Code (ASC) Suffix Rule**: In `Station_Entries` and `Station_Exits`, retain stations whose Alpha Station Code ends with lowercase `u` (e.g., `ACTu` for Acton Town LU, `WLOu` for Waterloo LU). Non-LU stations (e.g., `ACCr` for Acton Central rail, `ADVt` for Addington Village tram, `ABRd` for Abbey Road DLR) are filtered out.
3. **Line Identity & Link Coding**: In `Link_Loads` and `Link_Frequencies`, filter line names to the 10 Tube lines (`Bakerloo`, `Central`, `District`, `H&C and Circle`, `Jubilee`, `Metropolitan`, `Northern`, `Piccadilly`, `Victoria`, `Waterloo & City`).

---

## 3. Mathematical Metric Definitions

### 3.1 Passenger Load Per Train ($LPT$)
$$\text{LPT}_{i, p} = \frac{\text{Passenger Link Load}_{i, p}}{\text{Train Frequency}_{i, p}}$$
- $i$: Track link segment between consecutive stations
- $p$: Time period (e.g., AM Peak, PM Peak)
- *Note:* This represents the average number of passengers carried per train. It is a capacity proxy, not an absolute utilization percentage, as rolling stock capacities vary by line.

### 3.2 Congestion Classification Thresholds
Based on AM Peak load per train:
- **Low**: $0 \le \text{LPT} < 200$
- **Moderate**: $200 \le \text{LPT} < 500$
- **High**: $500 \le \text{LPT} < 800$
- **Critical**: $\text{LPT} \ge 800$

### 3.3 Service Adequacy Index ($SAI$)
$$\text{SAI}_{i} = \widetilde{D}_{i} \times (1 - \widetilde{F}_{i}) \times \widetilde{\text{LPT}}_{i} \times 100$$
- $\widetilde{D}_{i}$: Min-Max normalized total daily demand
- $\widetilde{F}_{i}$: Min-Max normalized AM peak service frequency
- $\widetilde{\text{LPT}}_{i}$: Min-Max normalized AM peak load per train
- Scale: $0$ (Well Served) to $100$ (Severely Underserved).

---

## 4. Graph Centrality & Optimization Scenarios
Network modeled as directed graph $G = (V, E)$, with $|V| = 270$ stations and $|E| \approx 700$ directed links.
- **Betweenness Centrality**:
  $$C_B(v) = \sum_{s \ne v \ne t} \frac{\sigma_{st}(v)}{\sigma_{st}}$$
- **Bottleneck Identification**: Segments where AM peak load $\ge P_{75}$, load per train $\ge P_{75}$, and frequency $\le P_{25}$.
- **Service Optimization Scenario**: Simulate a targeted $+25\%$ headway frequency augmentation on identified bottleneck links.

