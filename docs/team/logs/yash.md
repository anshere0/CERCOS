# Weekly log — Yash (Backend, Data Pipelines & Spatial Database Engineer)

## Week 1 (15 Jan – 21 Jan)
- **Hours:** 8
- **Done:** Defined SQLAlchemy 2.0 ORM models for all 8 database tables under schema `cercos` in `backend/app/models/` matching `contracts/schema.sql`. Created Pydantic v2 schemas for stations, vehicles, field data, and recommendations. Implemented automated schema drift test (`test_schema_drift.py`) with 100% column parity. Reviewed Ansh's Migration 0001 column-by-column against contract. Authored `docs/API.md`. (Branch: `feat/db-models`)
- **In progress:** OpenStreetMap Overpass API ingestion pipeline.
- **Blockers (who can unblock):** None.
- **Plan for next week:** Build Overpass QL query builder, coordinate extraction, socket tag normalizer, and etl_rejects quarantine table handling.
- **Supervisor signature date (record book):** 21 Jan 2026

## Week 2 (22 Jan – 28 Jan)
- **Hours:** 7
- **Done:** Implemented `backend/app/etl/osm_stations.py` with Overpass QL query builder for Bhopal urban area (100km radius) and MP bounding box. Added node and way centroid coordinate extraction, socket tag normalization to standard CERCOS connectors, and quarantine handling for malformed coordinates into `cercos.etl_rejects`. Authored unit tests with recorded mock fixtures in `test_osm_loader.py` (5 tests passing). (Branch: `feat/etl-osm`)
- **In progress:** Open Charge Map REST ingestion and spatial deduplication.
- **Blockers (who can unblock):** None.
- **Plan for next week:** Open Charge Map client and 50m Haversine distance spatial clustering engine.
- **Supervisor signature date (record book):** 28 Jan 2026

## Week 3 (29 Jan – 04 Feb)
- **Hours:** 8
- **Done:** Implemented Open Charge Map (OCM) ingestion client and 50m spatial deduplication engine in `backend/app/etl/ocm_stations.py`. Applied Haversine distance formula to cluster physical facilities within 50 meters, merging distinct connectors and elevating confidence to 0.95 for corroborated stations. Authored deduplication unit tests in `test_ocm_dedupe.py` (4 tests passing). (Branch: `feat/etl-ocm-dedupe`)
- **In progress:** District GeoJSON, VAHAN CSV, and field census loaders.
- **Blockers (who can unblock):** None.
- **Plan for next week:** Ingest MP administrative district boundaries, MoRTH VAHAN 4.0 registration counts, and physical census audits.
- **Supervisor signature date (record book):** 04 Feb 2026

## Week 4 (05 Feb – 11 Feb)
- **Hours:** 7
- **Done:** Implemented `backend/app/etl/districts_geojson.py` for MP district administrative boundaries and model EV city flagging. Implemented `backend/app/etl/vahan_csv.py` enforcing strict non-negative integer constraints on vehicle registrations. Implemented `backend/app/etl/census_import.py` for high-confidence (0.90) mobile field audits. Authored unit test suite in `test_loaders.py` (4 tests passing). (Branch: `feat/etl-loaders`)
- **In progress:** Data quality audit reporter and corridor seed fixtures.
- **Blockers (who can unblock):** None.
- **Plan for next week:** Automated data quality report generator and 20-station offline seed fixture dataset for local development.
- **Supervisor signature date (record book):** 11 Feb 2026

## Week 5 (12 Feb – 18 Feb)
- **Hours:** 8
- **Done:** Developed automated data quality audit script `backend/app/etl/data_quality.py` and generated authoritative audit report in `docs/DATA_QUALITY.md`. Constructed offline 20-station corridor seed dataset in `db/seeds/fixture_stations.json` spanning the Bhopal – Sehore – Ashta – Dewas – Indore corridor with complete attributes. Built idempotent database seeder `seed_fixtures.py` and unit tests in `test_data_quality.py` (3 tests passing). (Branch: `feat/data-quality-seed`)
- **In progress:** REST API endpoints implementation.
- **Blockers (who can unblock):** None.
- **Plan for next week:** Implement `/v1/modes`, `/v1/vehicles`, `/v1/stations`, `/v1/field`, and `/v1/recommend` endpoints.
- **Supervisor signature date (record book):** 18 Feb 2026

## Week 6 (19 Feb – 25 Feb)
- **Hours:** 9
- **Done:** Implemented FastAPI REST endpoints: `GET /v1/modes` returning 6 decision modes and criteria weights; `GET /v1/vehicles` returning technical charging parameters with segment filtering; `GET /v1/stations` returning GeoJSON `FeatureCollection` with bounding box filtering and full provenance; `GET /v1/stations/{id}` with 404 handler; `POST /v1/field/census`, `/survey` (with informed consent validation gate and strict zero PII rule), `/queue`; and `GET /v1/field/export/{kind}` streaming CSV output. (Branch: `feat/api-read`)
- **In progress:** Recommendation engine wrapper and OpenAPI export.
- **Blockers (who can unblock):** None.
- **Plan for next week:** Integrate MCDM TOPSIS wrapper in `/v1/recommend`, export live OpenAPI 3.1.0 schema, and execute performance budget verification.
- **Supervisor signature date (record book):** 25 Feb 2026

## Week 7 (26 Feb – 04 Mar)
- **Hours:** 8
- **Done:** Implemented `POST /v1/recommend` endpoint wrapping the MCDM engine interface, enforcing the physical bottleneck law $P_{\text{eff}} = \min(P_{\text{station}}, P_{\text{vehicle}})$, reserve SoC threshold (8%), and deterministic TOPSIS ranking. Exported live OpenAPI 3.1.0 JSON schema to `docs/openapi.json`. Verified performance budget (p95 latency < 500 ms for 200 candidate stations). Executed complete test suite (all 35 unit and contract tests passing) and achieved zero Ruff lint errors across the backend. (Branch: `feat/api-read`)
- **In progress:** Phase-I submission and peer review sign-offs with Anshuman and Atharva.
- **Blockers (who can unblock):** None.
- **Plan for next week:** Phase-I faculty presentation, viva defense, and Phase-II planning.
- **Supervisor signature date (record book):** 04 Mar 2026
