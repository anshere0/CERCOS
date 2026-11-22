# P1 — Data pipeline
Build `backend/app/etl/` with idempotent jobs:
1. `osm_stations.py` — Overpass query amenity=charging_station within MP bbox (and a Bhopal-100km polygon); map tags
   (operator, capacity, socket:* ) to our schema; confidence=0.5; source='osm'.
2. `ocm_stations.py` — Open Charge Map API (key from .env), India/MP filter, dedupe against OSM within 50 m (ST_DWithin).
3. `vahan_csv.py` — load district-wise EV registrations from manually exported Vahan dashboard CSVs placed in data/vahan/
   (document the exact export steps in docs/DATA_SOURCES.md). Do NOT scrape or call undocumented endpoints.
4. `districts_geojson.py` — load MP district boundaries (state source URL in docs/DATA_SOURCES.md, check licence).
5. `census_import.py` — import the field-census CSV/Google-Form export (columns listed in docs/FIELD_FORMS.md).
Add `make seed` that loads a small committed fixture (marked source='fixture') so the app runs offline.
Tests: dedupe, idempotency, provenance fields present, bad rows quarantined to `etl_rejects`.
Acceptance: row counts logged; a data-quality report (nulls, duplicates, out-of-bbox) written to docs/DATA_QUALITY.md.
