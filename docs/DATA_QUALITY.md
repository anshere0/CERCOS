# CERCOS Data Quality & Audit Report

**Author:** Yash (Backend, Data Pipelines & Spatial Database Engineer)  
**Corridor Focus:** Bhopal – Sehore – Ashta – Dewas – Indore (Madhya Pradesh)  
**Study Corridor Bounding Box:** `[22.5°N, 75.5°E] to [23.5°N, 77.8°E]`  
**Last Audit Execution:** `2026-02-18T12:00:00Z`  
**Status:** Validated Pipeline Output  

---

## 1. Executive Summary & Inventory

The CERCOS spatial database integrates heterogeneous charging infrastructure datasets across OpenStreetMap (OSM), Open Charge Map (OCM), field hardware census audits, and corridor seed fixtures.

- **Total Ingested Corridor Fixtures:** 20
- **Total Physical Connectors:** 30
- **Stations Within Study Corridor:** 20 (100.0%)
- **Stations Out of Corridor Bounding Box:** 0
- **Malformed / Invalid Coordinate Rejects:** 0
- **Potential Duplicate Clusters (< 50m):** 0
- **Mean Data Provenance Confidence:** `0.90`
- **High-Confidence Stations (>= 0.90):** 20 (100.0%)

---

## 2. Ingestion Source Distribution

| Source Identifier | Station Count | Percentage of Total | Provenance Confidence |
|---|:---:|:---:|:---:|
| `fixture` | 20 | 100.0% | 0.90 (Ground-Truth Calibrated) |
| `census` | Multi-point | Ingest Ready | 0.90 (Physical Audit Verified) |
| `osm` | Buffered | Ingest Ready | 0.80 (OpenStreetMap Single-source) |
| `ocm` | REST Synced | Ingest Ready | 0.85 (Open Charge Map Single-source) |
| `corroborated` | Spatial Joined | 50m Deduplicated | 0.95 (Multi-source Corroborated) |

---

## 3. Attribute Completeness & Quality Analysis

| Attribute | Available Count | Missing Count | Completeness Ratio |
|---|:---:|:---:|:---:|
| Geographic Coordinates | 20 | 0 | 100.0% |
| Operator / CPO Name | 20 | 0 | 100.0% |
| Max Power (kW) | 20 | 0 | 100.0% |
| Tariff (₹/kWh) | 20 | 0 | 100.0% |
| User Rating | 20 | 0 | 100.0% |
| Physical Address | 20 | 0 | 100.0% |
| Operational Status | 20 | 0 | 100.0% |
| Connectors Defined | 20 | 0 | 100.0% |

---

## 4. Spatial Clustering & Deduplication Metrics

The automated deduplication engine enforces a strict 50-meter Haversine spatial radius check:
- Distance metric:
  $$\Delta\sigma = 2 \arcsin \sqrt{\sin^2\left(\frac{\Delta\phi}{2}\right) + \cos\phi_1 \cos\phi_2 \sin^2\left(\frac{\Delta\lambda}{2}\right)}$$
  $$d = R \cdot \Delta\sigma \quad \text{where } R = 6371000 \text{ meters}$$
- All physical facilities located within 50 meters are consolidated into unified station profiles.
- Single-source entries enter with baseline confidence ($0.80$ for OSM, $0.85$ for OCM). Multi-source corroboration elevates confidence to $0.95$.
- Unresolved duplicate pairs remaining: **0**.

---

## 5. Compliance & Handoff Sign-off

- **Anshuman (Frontend Lead):** Verified clean GeoJSON feature properties with non-null coordinates.
- **Atharva (MCDM Lead):** Numeric power ratings and connector types validated for $P_{\text{eff}}$ calculation.
- **Eshwari (Empirical Report):** Verified corridor coverage figures ready for academic Phase-I report incorporation.
