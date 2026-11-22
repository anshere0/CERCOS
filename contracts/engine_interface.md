# Engine interface contract (Atharva implements, Yash consumes, Anshuman displays)
Function (pure, no DB/HTTP): `recommend(request, stations, vehicle, weights, bounds) -> RecommendResult`

**request:** `{ origin:{lat,lon}, destination:{lat,lon}, soc_pct:float, mode:str, segment:str, vehicle_id:int|null, route_km:float, route_geojson:object|null }`
**station (input rows):** `{ station_id, name, cpo_name, lat, lon, max_power_kw, tariff_inr_kwh, rating, is_operational, connector_types:[str], detour_km, km_along_route, predicted_wait_min, source, confidence }`
**vehicle:** `{ segment, battery_kwh, wh_per_km, max_dc_kw, max_ac_kw, connector_types:[str] }`
**result:**
```
{ needs_charging: bool,
  reachable_km: float,
  top3: [ { station_id, name, score, rank,
            eta_extra_min, est_cost_inr, est_charge_min, arrival_soc_pct,
            criteria:{detour_km,cost_inr_kwh,wait_min,effective_kw,rating,arrival_soc_pct},
            explain:[ {criterion, contribution, note} ],
            source, confidence } ],
  rejected: [ {station_id, reason} ],     # connector mismatch / not operational / unreachable
  warnings: [str],                         # e.g. "routing fallback: haversine x1.3", "synthetic data used"
  engine_version: str }
```
Rules: effective_kw = min(max_power_kw, vehicle max kW for that connector type); anchored bounds from config/criteria_bounds.yaml; weights from config/weights.yaml; reserve = 8% SoC; scoring must be deterministic.
