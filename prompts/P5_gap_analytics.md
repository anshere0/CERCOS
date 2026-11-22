# P5 — Infrastructure-gap analytics (AFTER the Phase-I cut line; run only after P4 is reviewed)
Backend jobs + endpoints + dashboard pages:
1. District table: EVs by class (Vahan), stations, connectors, DC-fast share, EV-per-connector, per-100 km2 density.
2. Corridor gap finder: for each highway polyline (NH-46 Bhopal-Ashta-Indore stretch, Bhopal-Narmadapuram, Bhopal-Vidisha-Sanchi) snap stations,
   compute inter-station spacing, flag segments > 25 km (MoP norm) and > 100 km for fast-charging; output GeoJSON + CSV.
3. Urban coverage: 3x3 km grid over Bhopal city; flag empty cells; compute % coverage.
4. Accessibility: two-step floating catchment area (2SFCA) score per grid cell using EV demand proxy.
5. Candidate-site ranking v0: maximal-covering heuristic (greedy p-median/MCLP) choosing k new sites; show marginal coverage gain; every output cites inputs and confidence.
Dashboard (Recharts + map): choropleth, corridor gap bars, coverage KPI cards, export-to-PDF for the faculty report.
Acceptance: fixtures prove gap detection; all charts show data provenance badges; docs/GAP_METHOD.md explains each metric.
