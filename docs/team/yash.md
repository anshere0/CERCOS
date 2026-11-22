# YASH — Data Pipelines, Database Models & Backend API  (8% of the 40%)

**Mission:** real station and EV data flows into PostGIS with provenance, and the API exposes it, field forms and the engine's recommendation to the frontend. You own the road between the data and the screen.
Your PRs are reviewed by **Anshuman** (primary, as the API's first consumer) and **Atharva** (secondary). You review **Atharva** (primary), **Ansh** and **Anshuman** (secondary).

## You own
`backend/app/etl/` · `backend/app/api/` · `backend/app/models/` · `backend/app/schemas/` · `backend/tests/etl/` · `backend/tests/api/` · `db/seeds/` · `docs/DATA_QUALITY.md` · `docs/API.md` · `docs/DATA_SOURCES.md` (final pass; Eshwari writes the first draft)
You co-sign `contracts/schema.sql` and `contracts/openapi.draft.yaml` with Ansh and Atharva.

## Inputs / Outputs
| You need | From | When |
|---|---|---|
| Alembic migration 0001 | Ansh | 28 Nov |
| Vahan district CSVs, district GeoJSON | Eshwari | 6–13 Dec |
| Census CSV format and files | Kashish | format W1, data W5+ |
| `recommend()` | Atharva | 20 Dec |
| **You deliver** | | |
| Models, loaders, seed fixture | everyone | 6–20 Dec |
| Working endpoints | Anshuman | **20 Dec** (mock-first before) |
| Station table export for the corridor script | Eshwari | 14 Dec |
| API tests, OpenAPI export, data snapshot | everyone | 3–10 Jan |

## Task list by week
**W1:** SQLAlchemy 2 models matching `contracts/schema.sql` exactly; review Ansh's migration (every column, constraint and index). Mismatch? Open an issue the same day.
**W2:** `osm_stations.py` (Overpass `amenity=charging_station`, Bhopal-100 km polygon and MP bbox) with `source='osm'`, `confidence=0.5`, `fetched_at`; bad rows go to `etl_rejects`. `ocm_stations.py` (key from `.env`, never committed) and dedupe against OSM with `ST_DWithin` 50 m.
**W3:** loaders: `districts_geojson.py`, `vahan_csv.py` (reads `data/vahan/*.csv`, **no scraping**), `census_import.py`.
**W4:** `docs/DATA_QUALITY.md` generator (nulls, duplicates, out-of-bbox); seed fixture (`source='fixture'`). API: `/v1/modes`, `/v1/vehicles`, `/v1/stations` (bbox, GeoJSON with provenance), `/v1/stations/{id}`, `/v1/field/census|survey|queue` + CSV export. Survey endpoint rejects `consent=false`.
**W5:** `/v1/recommend`: load candidate stations, compute detour and distance via OSRM (fallback haversine×1.3 plus warning), call `recommend()`, log to `recommendations_log`.
**W6:** API tests; load test: **p95 < 500 ms** for 200 candidate stations; export the OpenAPI JSON to `docs/openapi.json`.
**W7:** freeze a data snapshot with row counts for the report; finish `docs/DATA_SOURCES.md` and `docs/API.md`.

## Commit trajectory
| Branch | Commits | PR title | Reviewer | Due |
|---|---|---|---|---|
| `feat/db-models` | `feat(db): add SQLAlchemy models from contract` → `test(db): model smoke tests` | DB models | Anshuman | 29 Nov |
| `feat/etl-osm` | `feat(etl): add Overpass loader` → `feat(etl): add reject table handling` → `test(etl): osm loader fixtures` | OSM ingest | Atharva | 4 Dec |
| `feat/etl-ocm-dedupe` | `feat(etl): add Open Charge Map loader` → `feat(etl): dedupe within 50 m` → `test(etl): dedupe tests` | OCM ingest + dedupe | Atharva | 6 Dec |
| `feat/etl-loaders` | `feat(etl): districts loader` → `feat(etl): vahan csv loader` → `feat(etl): census import` | District, Vahan, census loaders | Atharva | 13 Dec |
| `feat/data-quality-seed` | `feat(etl): data quality report` → `data(seeds): add fixture stations` | Data quality + seed | Atharva | 20 Dec |
| `feat/api-read` | `feat(api): modes and vehicles` → `feat(api): stations bbox geojson` → `feat(api): station detail` → `test(api): read endpoints` | Read endpoints | Anshuman | 20 Dec |
| `feat/api-field` | `feat(api): census endpoint` → `feat(api): survey endpoint with consent check` → `feat(api): queue endpoint` → `feat(api): csv export` | Field endpoints | Anshuman | 20 Dec |
| `feat/api-recommend` | `feat(api): osrm client with fallback` → `feat(api): recommend endpoint` → `test(api): recommend contract` | /v1/recommend | Anshuman | 27 Dec |
| `test/api-perf` | `test(api): p95 latency for 200 stations` → `docs(api): export openapi` | API tests + OpenAPI | Anshuman | 3 Jan |
| `docs/data-final` | `docs(data): final sources and snapshot` | Data docs | Atharva | 10 Jan |

## Definition of Done
- Every row in `charging_stations`, `districts` and `vehicles` has `source`, `fetched_at`, `confidence`; synthetic rows are flagged.
- Re-running any loader is **idempotent** (no duplicates).
- All endpoints in `contracts/openapi.draft.yaml` exist and are tested; `/docs` shows them.
- `/v1/recommend` returns the structure from `contracts/engine_interface.md`.
- p95 < 500 ms for 200 stations on local docker; routing fallback is reported in `warnings`.
- No API keys or raw personal data in the repository.

## Antigravity prompt (Planning mode, branch `feat/etl-osm`, adapt per task)
```
Read AGENTS.md, contracts/schema.sql, contracts/openapi.draft.yaml and contracts/engine_interface.md.
You work for Yash. Edit ONLY backend/app/etl/, backend/app/api/, backend/app/models/, backend/app/schemas/, backend/tests/etl/, backend/tests/api/, db/seeds/, docs/DATA_QUALITY.md, docs/API.md.
Task: implement an idempotent Overpass loader for amenity=charging_station inside the MP bounding box and a Bhopal 100 km polygon. Map tags (operator, capacity, socket:*) to our schema, set source='osm', confidence=0.5, fetched_at=now. Rows missing coordinates go to etl_rejects with a reason. Use only documented public endpoints; respect rate limits; no scraping of other sites.
Write tests with recorded fixtures (no live network in tests). Plan first, small commits as in docs/team/yash.md. Do not touch other folders. Do not push to main.
```

## Report evidence (your half page)
Data sources and licences, ETL design, provenance model, row counts per source, API design, latency results — with links to merged PRs.
