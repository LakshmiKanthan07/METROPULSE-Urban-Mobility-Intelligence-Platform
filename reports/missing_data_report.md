# METROPULSE — Data Availability & Missing Data Audit Report
## Comprehensive Audit of Official TfL NUMBAT Datasets (2023–2025)

### Executive Summary
A total of **22 core urban mobility metrics** were systematically audited against the 15 official TfL NUMBAT workbooks.

| Availability Status | Metric Count | Percentage |
|---|:---:|:---:|
| **AVAILABLE** | 11 | 50.0% |
| **DERIVABLE** | 3 | 13.6% |
| **UNAVAILABLE** | 2 | 9.1% |
| **REQUIRES USER INPUT** | 2 | 9.1% |
| **REQUIRES EXTERNAL DATA** | 2 | 9.1% |
| **PARTIALLY AVAILABLE** | 1 | 4.5% |
| **NOT APPLICABLE** | 1 | 4.5% |

---

### Detailed Audit of Missing, Partial & External-Dependent Metrics

#### Passenger Origin-Destination Matrix (`PARTIALLY AVAILABLE`)
- **Category**: Passenger Analytics
- **Description**: Full end-to-end station-pair (O-D) passenger journey flows across the complete network.
- **Dashboard Location**: `2_Demand_Analysis`
- **Why Missing/Partial in NUMBAT**: Network-wide OD chord diagrams cannot show complete multi-line trips
- **Suggested Authoritative External Source**: TfL Open Data: Origin-Destination Journey Matrices
- **User Input Requirement**: Approval to restrict display to Station Complex Interchanges rather than full city trips
- **Strict Data Integrity Policy**: Clearly label as 'Station Complex Movements' and note OD survey requirement

#### Actual Train Crush Capacity (`UNAVAILABLE`)
- **Category**: Service Analytics
- **Description**: Physical passenger carrying capacity of train rolling stock by line (seated + standing).
- **Dashboard Location**: `3_Congestion`
- **Why Missing/Partial in NUMBAT**: Absolute crowding % (occupancy rate) cannot be displayed; must use relative LPT and SAI
- **Suggested Authoritative External Source**: TfL Rolling Stock Fleet Specifications (e.g. Victoria 2009 Tube Stock: ~1,194 max crush capacity)
- **User Input Requirement**: User approval of nominal rolling stock capacity parameter (e.g., 1,000 pax/train) or external specification lookup table
- **Strict Data Integrity Policy**: Display 'Requires External Dataset' and present relative Load-Per-Train instead of unverified % occupancy

#### Train Occupancy Percentage (`UNAVAILABLE`)
- **Category**: Service Analytics
- **Description**: Passenger load divided by physical train design capacity (% full).
- **Dashboard Location**: `3_Congestion`
- **Why Missing/Partial in NUMBAT**: Absolute percentage fullness cannot be asserted without violating data integrity
- **Suggested Authoritative External Source**: TfL Rolling Stock Fleet Manual
- **User Input Requirement**: User input on whether to use nominal capacity estimates or suppress metric
- **Strict Data Integrity Policy**: Strict adherence to Data Integrity Rule: Suppress fake occupancy % and show Load-Per-Train

#### Real-Time Train Delays & Disruptions (`NOT APPLICABLE`)
- **Category**: Service Analytics
- **Description**: Real-time unplanned signal failures, track delays, and headways deviation.
- **Dashboard Location**: `3_Congestion`
- **Why Missing/Partial in NUMBAT**: No real-time delay tracking (out of scope for static NUMBAT analysis)
- **Suggested Authoritative External Source**: TfL Unified API (https://api.tfl.gov.uk/Line/Mode/tube/Status)
- **User Input Requirement**: None
- **Strict Data Integrity Policy**: Display 'Planning Model: Real-Time Delays Not Applicable' badge

#### Official PTAL (Public Transport Accessibility Level) (`REQUIRES EXTERNAL DATA`)
- **Category**: Geospatial Analytics
- **Description**: Official London-wide PTAL index (0 to 6b) assessing multi-modal walking accessibility.
- **Dashboard Location**: `4_Geospatial`
- **Why Missing/Partial in NUMBAT**: Official multi-modal PTAL score cannot be asserted without full bus/rail network data
- **Suggested Authoritative External Source**: TfL Planning Information Database / WebCAT GIS Data
- **User Input Requirement**: Approval to present 'Underground Inter-Station Spacing Index' as empirical proxy rather than claiming official multi-modal PTAL
- **Strict Data Integrity Policy**: Show empirical 'Tube Isolation & Spacing Score' and label official PTAL as 'Requires External Dataset'

#### External Macro Explanatory Variables (Weather/GDP/Strikes) (`REQUIRES EXTERNAL DATA`)
- **Category**: Machine Learning
- **Description**: Rainfall, temperature, inflation, hybrid work mandates, industrial strike days.
- **Dashboard Location**: `5_Machine_Learning`
- **Why Missing/Partial in NUMBAT**: Weather elasticity cannot be estimated directly from typical-day profiles
- **Suggested Authoritative External Source**: Met Office MIDAS / ONS Labor Market Statistics
- **User Input Requirement**: Approval to restrict features to topological and profile features (year, day_type, central distance, fare zone)
- **Strict Data Integrity Policy**: Document as an external data opportunity; rely on verified network topology features

#### Maximum Signaling Headway Limits (`REQUIRES USER INPUT`)
- **Category**: Optimization
- **Description**: Maximum trains per hour physically permitted by signaling system by line (e.g. 36 tph on Victoria).
- **Dashboard Location**: `6_Optimization`
- **Why Missing/Partial in NUMBAT**: Optimization could hypothetically schedule an impossible number of trains (e.g. 60 tph)
- **Suggested Authoritative External Source**: TfL Signaling Engineering Standards (CBTC / DTG / SelTrac)
- **User Input Requirement**: Approval of maximum frequency cap parameter (Default recommended: 36 tph for automatic lines, 30 tph for conventional lines)
- **Strict Data Integrity Policy**: Set realistic default caps (36 tph) with clear transparency note in UI

#### Fleet & Depot Operational Constraints (`REQUIRES USER INPUT`)
- **Category**: Optimization
- **Description**: Available spare train sets, driver crew rosters, and depot maintenance capacity.
- **Dashboard Location**: `6_Optimization`
- **Why Missing/Partial in NUMBAT**: Must clearly identify scenario as hypothetical decision support, not approved operational timetable
- **Suggested Authoritative External Source**: TfL Operations Planning
- **User Input Requirement**: Approval to treat +25% headway relief as an analytical 'Unconstrained Fleet Scenario'
- **Strict Data Integrity Policy**: Label scenario simulation prominently as 'SIMULATED SCENARIO — UNCONSTRAINED FLEET ASSUMPTION'
