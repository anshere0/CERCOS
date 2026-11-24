# CERCOS REST API Specification & Contract

**Author:** Yash (Backend & Spatial Database Engineer)  
**Contract Baseline:** `contracts/openapi.draft.yaml` & `contracts/engine_interface.md`  
**Status:** Active Implementation Specification  

---

## 1. Overview
The CERCOS REST API exposes high-performance, validated endpoints serving geospatial charging infrastructure, vehicle specifications, driver decision modes, anonymous field research telemetry, and algorithmic charging recommendations across the Bhopal – Indore corridor.

All endpoints are served under prefix `/v1` (with `/health` at root).

---

## 2. Endpoints Catalog

### 2.1 System Health
- **`GET /health`**
  - **Summary:** Service liveness probe.
  - **Responses:** `200 OK` `{"status": "ok"}`

### 2.2 Core Catalog & Reference Data
- **`GET /v1/modes`**
  - **Summary:** Lists 6 standardized driver decision modes and default BWM criteria weights (Cheapest, Fastest, Shortest, HighestRated, BatterySafe, Balanced).
  - **Responses:** `200 OK`

- **`GET /v1/vehicles`**
  - **Summary:** Lists vehicle intake technical profiles (battery capacity, consumption, maximum DC/AC power, connectors).
  - **Query Parameters:** `segment` (Optional: `E2W`, `E3W`, `E4W`, `ELCV`).
  - **Responses:** `200 OK`

### 2.3 Geospatial Charging Stations
- **`GET /v1/stations`**
  - **Summary:** Spatial bounding box query returning GeoJSON `FeatureCollection` with complete provenance attributes (`source`, `confidence`, `fetched_at`).
  - **Query Parameters:**
    - `bbox` (Required): `minLon,minLat,maxLon,maxLat` (e.g. `76.5,22.8,77.8,23.5`).
    - `source` (Optional): Filter by `osm`, `ocm`, `census`, `fixture`.
  - **Responses:** `200 OK` (GeoJSON `FeatureCollection`)

- **`GET /v1/stations/{id}`**
  - **Summary:** Detailed profile lookup for a specific charging station.
  - **Responses:** `200 OK`, `404 Not Found`

### 2.4 Field Research & Data Intake
- **`POST /v1/field/census`**
  - **Summary:** Ingests field hardware census audit for physical charging stations.
  - **Responses:** `201 Created`

- **`POST /v1/field/survey`**
  - **Summary:** Submits driver BWM pairwise comparison responses.
  - **Privacy & Consent Gate:** Enforces `consent: true`. If `consent: false` or missing, rejects with `422 Unprocessable Entity`.
  - **Anonymity Rule:** Strictly forbids personal identifiers (names, phone numbers, vehicle registrations).
  - **Responses:** `201 Created`, `422 Unprocessable Entity`

- **`POST /v1/field/queue`**
  - **Summary:** Ingests 3-hour queuing observations (`07-10`, `12-15`, `18-21`).
  - **Responses:** `201 Created`

- **`GET /v1/field/export/{kind}`**
  - **Summary:** Streams CSV export of field telemetry data (`census`, `survey`, or `queue`).
  - **Responses:** `200 OK` (`text/csv`)

### 2.5 Algorithmic Recommendation Engine
- **`POST /v1/recommend`**
  - **Summary:** Recommends optimal charging stops along route via TOPSIS & M/G/c queueing simulation.
  - **Core Rule:** Effective power bottleneck: $P_{\text{eff}} = \min(P_{\text{station}}, P_{\text{vehicle}})$.
  - **Responses:** `200 OK` (`RecommendResult`), `422 Unprocessable Entity`
