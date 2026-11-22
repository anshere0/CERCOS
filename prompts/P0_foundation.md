# P0 — Foundation (Planning mode)
Create the monorepo: `backend/` (FastAPI, SQLAlchemy 2, Alembic), `frontend/` (React+Vite+TS), `db/` (init SQL),
`config/` (weights.yaml, criteria_bounds.yaml, vehicles.yaml), `research/`, `docs/`, `docker-compose.yml`
(postgis/postgis:16-3.4, api, web), Makefile (`up`, `test`, `seed`, `lint`), GitHub Actions CI, `.env.example`.
Schema (Alembic migration 0001): districts(geom MultiPolygon 4326, rto_code, ev counts by class, is_model_ev_city),
charging_stations(cpo_name, name, district_id, address, max_power_kw, tariff_inr_kwh, rating, is_operational,
hours, contact, geom Point, source, fetched_at, confidence), connectors(station_id, type, kw, status),
vehicles(model, segment, battery_kwh, wh_per_km, max_dc_kw, max_ac_kw, connector_types[]),
survey_responses(...), station_observations(station_id, ts, queue_len, busy_connectors, session_minutes, observer),
recommendations_log(...). GiST indexes on all geometries.
Seed `config/vehicles.yaml` with 6 reference vehicles across E2W/E3W/E4W (mark specs `confidence` and cite the manufacturer sheet URL in a comment; leave unknown values null rather than guessing).
Acceptance: `docker compose up` healthy; `GET /health` ok; migrations apply; CI green.
