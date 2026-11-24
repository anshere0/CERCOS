# CERCOS Data Quality & Audit Report

**Author:** Yash (Backend, Data Pipelines & Spatial Database Engineer)  
**Corridor Focus:** Bhopal – Sehore – Ashta – Dewas – Indore (Madhya Pradesh)  
**Study Corridor Bounding Box:** `[22.5°N, 75.5°E] to [23.5°N, 77.8°E]`  
**Last Audit Execution:** `2026-11-24T19:48:43.029162+00:00`  
**Status:** Validated Pipeline Output  

---

## 1. Executive Summary & Inventory

The CERCOS spatial database integrates heterogeneous charging infrastructure datasets across OpenStreetMap (OSM), Open Charge Map (OCM), field hardware census audits, and corridor seed fixtures.

- **Total Ingested Stations:** 508
- **Total Physical Connectors:** 1259
- **Stations Within Study Corridor:** 445 (87.6%)
- **Stations Out of Corridor Bounding Box:** 63
- **Malformed / Invalid Coordinate Rejects:** 0
- **Potential Duplicate Clusters (< 50m):** 0
- **Mean Data Provenance Confidence:** `0.866`
- **High-Confidence Stations (>= 0.90):** 237

---

## 2. Ingestion Source Distribution

| Source Identifier | Station Count | Percentage of Total |
|---|:---:|:---:|
| `ocm` | 506 | 99.6% |
| `osm` | 2 | 0.4% |

---

## 3. Attribute Completeness & Quality Analysis

| Attribute | Available Count | Missing Count | Completeness Ratio |
|---|:---:|:---:|:---:|
| Geographic Coordinates | 508 | 0 | 100.0% |
| Operator / CPO Name | 503 | 5 | 99.0% |
| Max Power (kW) | 508 | 0 | 100.0% |
| Tariff (₹/kWh) | 202 | 306 | 39.8% |
| User Rating | 0 | 508 | 0.0% |
| Physical Address | 508 | 0 | 100.0% |

---

## 4. Spatial Clustering & Deduplication Metrics

The automated deduplication engine enforces a strict 50-meter Haversine spatial radius check:
- Distance metric: $d = 2R \arcsin \sqrt{\sin^2(\Delta\phi/2) + \cos\phi_1\cos\phi_2\sin^2(\Delta\lambda/2)}$
- All physical facilities located within 50 meters are consolidated into unified station profiles.
- Single-source entries enter with baseline confidence ($0.80$ for OSM, $0.85$ for OCM). Multi-source corroboration elevates confidence to $0.95$.
- Unresolved duplicate pairs remaining: **0**.

---

## 5. Compliance & Handoff Sign-off

- **Anshuman (Frontend Lead):** Verified clean GeoJSON feature properties with non-null coordinates.
- **Atharva (MCDM Lead):** Numeric power ratings and connector types validated for $P_{\text{eff}}$ calculation.
- **Eshwari (Empirical Report):** Verified corridor coverage figures ready for academic Phase-I report incorporation.

---

## 6. Upstream Public Registry Provenance

- **Primary Registry:** `reclaimchennai/india-ev-charging-dataset` (merged Indian EV station snapshot from Kia/Numocity, MG eHUB, ChargeZone, Ather Grid, Bolt.Earth, OpenChargeMap, and OpenStreetMap).
- **Live OSM API v0.6 Nodes:** Verified corridor elements `13917513464, 13913881928, 13917515273, 13919645475` fetched directly from `https://api.openstreetmap.org/api/0.6/node/{id}.json` and deduplicated within 50m.
- **Explicit Missing-Field Policy:** Upstream pricing is preserved verbatim where present (including `₹0.0/kWh` for free stations) and stored as `null` when unlisted upstream (zero fabricated retail tariffs).
