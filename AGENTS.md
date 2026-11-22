# AGENTS.md — CERCOS (Cognitive EV Route & Charging Optimization System)

Read PROJECT_MANIFEST.yaml first. It is the single source of truth for scope, phases and acceptance tests.

## Mission
Recommend the *best* EV charging stop (not the nearest) for Madhya Pradesh drivers using multi-criteria
decision making (TOPSIS), and turn the same data into infrastructure-gap analytics for planners.
This is an EPICS community-service project: real users = e-2W/e-3W/e-4W drivers within 100 km of VIT Bhopal.

## Hard rules
1. NEVER fabricate real-world data. Anything simulated is tagged `source='synthetic'` and shown in the UI as "Simulated".
2. Every station/vehicle record carries `source`, `fetched_at`, `confidence` (0-1). Provenance is mandatory.
3. No scraping that violates a site's ToS/robots.txt. Allowed sources: OpenStreetMap (Overpass), Open Charge Map API,
   Vahan public dashboard CSV exports, government PDFs, and our own field survey data.
4. Scoring code is pure functions in `backend/app/mcdm/` with unit tests. No DB or HTTP calls inside scoring.
5. Speed criterion = min(station_kW, vehicle_max_accept_kW) — never raw station kW.
6. Normalisation must not cause rank reversal: use domain-anchored bounds from `config/criteria_bounds.yaml`
   (see research/01 results). Keep classic TOPSIS only as a comparison baseline.
7. Weights are config, not code (`config/weights.yaml`); the survey-derived weights (AHP/BWM) override the defaults.
8. Plan first (Planning mode), produce an implementation-plan artifact, wait for approval on schema/API changes.
9. Every phase ends with: tests green, `docs/PHASE_REPORT.md` updated, screenshots/recording artifact, and a git commit.
10. Secrets only in `.env` (git-ignored). Provide `.env.example`.

## Stack
FastAPI + SQLAlchemy 2 + Alembic · PostgreSQL 16 + PostGIS 3 · pgRouting/OSRM for road distance ·
React + Vite + TypeScript + Leaflet/MapLibre + Recharts · scikit-learn/pandas · Docker Compose · pytest + Playwright.

## Definition of done (project-wide)
`docker compose up` brings up db+api+web; `make test` passes; `make seed` loads demo data; `/docs` shows OpenAPI.

## Team ownership rules (apply to every agent session)
- This repository has six owners. Read `TEAM.md`, `CONTRIBUTING.md` and `.github/CODEOWNERS` first.
- An agent session works for ONE person on ONE branch. Edit only that person's folders. If a change is needed elsewhere, write it as an issue text, do not edit.
- Never push to `main`. Never merge. Commit messages follow Conventional Commits (see CONTRIBUTING.md).
- Respect `contracts/` and `config/`: do not change them without an issue approved by two people.
- Never commit anything under `data/field/raw/` or any personal data.
