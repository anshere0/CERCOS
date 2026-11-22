# P4 — API + Map MVP (single corridor)
API: `POST /v1/recommend` {origin, destination, vehicle_id|custom, soc_pct, mode, segment} ->
{needs_charging, top3[], route_geojson, explain[], warnings[]}; `GET /v1/stations?bbox=`, `GET /v1/stations/{id}`,
`GET /v1/modes`, `GET /v1/vehicles`. Road distance via OSRM (docker) with graceful fallback to haversine*1.3 flagged in warnings.
UI: React + MapLibre/Leaflet; form (origin, destination, vehicle, SoC, mode), result cards (score, cost, wait, arrival SoC,
"why this one"), route + station markers, station detail drawer (all fields from the project spec), badge for 'Simulated'/'Census'/'OSM' data.
Include a side-by-side "Nearest vs CERCOS" comparison panel — this is the demo for faculty.
Tests: API contract tests, Playwright e2e for the Bhopal->Ashta scenario; p95 < 500 ms for 200 stations.
Acceptance: record a browser walkthrough artifact.
