# METROPULSE — Analytical Assumptions & Limitations

## 1. Typical-Day Modeling vs. Real-Time Feeds
- **Limitation**: The NUMBAT dataset represents modeled *typical operating day profiles* rather than real-time tap-in event streams or continuous daily logs.
- **Analytical Safeguard**: The system does not attempt calendar date-time forecasting (e.g. predicting March 14, 2026). Instead, it estimates representative day-type passenger profiles using rigorous Leave-One-Year-Out validation.

## 2. Load per Train as a Capacity Proxy
- **Limitation**: NUMBAT provides passenger link loads and scheduled train frequencies, but does not provide vehicle crush capacity per individual trainset type.
- **Analytical Safeguard**: Passenger Load Per Train ($\text{LPT} = \text{Link Load} / \text{Train Frequency}$) is explicitly treated as a *relative vehicle crowding indicator*, not an absolute engineering capacity percentage.

## 3. Scheduled vs. Actual Operated Frequency
- **Limitation**: `Link_Frequencies` records scheduled service timetables. Signal delays, mechanical cancellations, or emergency headway gaps are not reflected in baseline NUMBAT figures.
- **Analytical Safeguard**: Bottleneck analysis explicitly highlights service-demand friction based on baseline scheduled capacity.

## 4. Optimization Scenario Scope
- **Limitation**: The $+25\%$ headway frequency scenario is an analytical simulation. Real-world implementation is subject to depot stabling capacity, power substation limits, driver crew rosters, and signaling block constraints.
- **Analytical Safeguard**: All recommendations are presented as strategic scenario explorations, not deployable operational working timetables.

