# ⚠️ METROPULSE — User Input & Decision Approval Register
## DataNova Global Data-thon 2026 | Problem Statement DN-DS-01

> [!IMPORTANT]
> **Strict Data Integrity Protocol**: In accordance with Section 2 of the Master Prompt, METROPULSE strictly prohibits fabricating, randomly generating, or silently substituting missing values. The following items represent values, external datasets, parameters, and analytical assumptions that require explicit user review and approval before they can be integrated into production results.

---

### 1. Essential Missing Information (Requiring Approval to Define Parameters)

#### Item 1.1: Maximum Signaling Frequency Caps by Line
- **Field / Parameter**: Maximum Permitted Trains Per Hour ($TPH_{max}$) for Optimization Scenarios.
- **Why Required**: Prevents the NetworkX route optimization simulator from proposing physically impossible schedules (e.g., >40 tph).
- **Where Used**: `dashboard/pages/6_Optimization.py`, `src/optimization/service_optimizer.py`.
- **Impact if Unavailable**: Default safety caps are used (36 tph for automatic lines like Victoria, 30 tph for conventional lines like Bakerloo/Piccadilly).
- **Expected Format & Unit**: Integer ($tph$ between 20 and 36).
- **Suggested Source**: TfL Signaling Engineering Asset Register.
- **Requires Approval**: **YES** — Confirm whether 36 tph (Victoria) and 30 tph (other lines) are accepted as standard engineering ceiling constraints.

#### Item 1.2: Nominal Train Crush Capacity by Rolling Stock
- **Field / Parameter**: Maximum passenger capacity per train ($Cap_{train}$).
- **Why Required**: Calculating absolute percentage train occupancy (% fullness).
- **Where Used**: `dashboard/pages/3_Congestion.py`.
- **Impact if Unavailable**: Absolute % fullness is **suppressed** to avoid fabricating metrics. The system displays relative **Load-Per-Train (LPT)** and **Service Adequacy Index (SAI)** instead.
- **Expected Format & Unit**: Integer passengers/train (e.g., 1,000 to 1,200).
- **Suggested Source**: TfL Rolling Stock Fleet Specifications.
- **Requires Approval**: **YES** — Decide whether to: (A) supply verified rolling stock capacities per line, (B) approve a standard benchmark parameter (e.g. 1,050 pax/train), or (C) keep absolute occupancy % suppressed in favor of observed LPT.

---

### 2. Optional Enhancements & Analytical Assumptions

#### Item 2.1: Full City-Wide Origin-Destination Matrices vs Station Complex Flows
- **Context**: NUMBAT `Station_Flows` captures interchange movements within complex stations (e.g. platform-to-platform transfers at Oxford Circus or Bank), but does NOT record individual journey origin-destination station pairs across the whole city.
- **Assumption Requiring Approval**: Approve displaying OD chord charts as *'Station Complex Interchange Movements'* rather than full multi-leg city trips.
- **Alternative**: Ingest external TfL RODS (Rolling Origin & Destination Survey).
- **Requires Approval**: **YES**.

#### Item 2.2: Tube Spacing Accessibility Proxy vs Official Multi-Modal PTAL
- **Context**: Official London PTAL (Public Transport Accessibility Levels) scores require walking networks, bus route schedules, and national rail feeds outside NUMBAT.
- **Assumption Requiring Approval**: Approve displaying the computed *'Underground Station Spacing & Distance Decay Index'* as an empirical Tube accessibility measure, while clearly indicating that official multi-modal PTAL requires external GIS layers.
- **Requires Approval**: **YES**.

---

### 3. External Datasets to Potentially Obtain (Future Roadmap)

| External Dataset | Authority / Source | Analytical Capability Unlocked | Priority |
|---|---|---|:---:|
| **TfL Rolling Stock Fleet Capacity Register** | TfL Engineering | Converts Load-Per-Train into exact % vehicle occupancy | High |
| **TfL Live Trackbot / Unified API Disruptions** | TfL Open Data | Overlays historical delays and signal incidents onto NUMBAT planned profiles | Medium |
| **TfL WebCAT Multi-Modal PTAL GIS Shapefiles** | TfL Planning | Adds full London-wide multi-modal accessibility layers (bus + tram + rail) | Medium |
| **Met Office London Climate & Weather Data** | Met Office MIDAS | Enables weather sensitivity elasticity regression in ML | Low |

---

### 4. Dashboard Features Currently Handled via Graceful Fallback States

In strict adherence to the **Data Integrity Principle**, the following UI states are actively rendered where source data is incomplete:
1. **Train Occupancy %**: Displays `[REQUIRES EXTERNAL CAPACITY DATA]` badge instead of a fabricated percentage.
2. **Real-Time Delays**: Displays `[PLANNING MODEL — REAL-TIME DELAYS NOT APPLICABLE]` badge.
3. **Multi-Modal Trips**: Labeled as `[STATION COMPLEX TRANSFERS ONLY — OD SURVEY REQUIRED FOR FULL TRIPS]`.
4. **Simulation Scenarios**: Prominently watermarked as `[SIMULATED SCENARIO — UNCONSTRAINED FLEET ASSUMPTION]`.

---
*Report generated automatically by METROPULSE Data Quality & Audit Engine.*