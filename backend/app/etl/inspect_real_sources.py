"""Inspect and fetch genuinely real EV charging stations for Madhya Pradesh."""
import json
import sys
from pathlib import Path

import httpx

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from app.etl.osm_stations import MP_BBOX, build_overpass_query

headers = {"User-Agent": "CERCOS-VIT-Bhopal-EPICS/1.0"}

# 1. Inspect mglsj/indian_ev_charging_stations repository files
r_gh = httpx.get(
    "https://api.github.com/repos/mglsj/indian_ev_charging_stations/contents/",
    headers=headers,
    timeout=15.0,
)
print("=== GitHub Indian EV Charging Stations Repo ===")
if r_gh.status_code == 200:
    for f in r_gh.json():
        print(f" - {f['name']} ({f['size']} bytes) -> {f.get('download_url')}")

# 2. Query Nominatim directly for category=amenity type=charging_station across Bhopal/Indore/MP boxes
print("\n=== Nominatim Real OSM charging_station POIs across MP ===")
mp_boxes = [
    ("Bhopal-Indore Corridor", "75.5,24.0,78.5,22.4"),
    ("MP North (Gwalior)", "77.0,26.8,79.5,25.5"),
    ("MP East (Jabalpur/Rewa)", "79.0,25.0,82.5,22.5"),
    ("MP West (Ujjain/Ratlam)", "74.5,24.5,76.5,22.0"),
]
nom_stations = {}
for label, vb in mp_boxes:
    for term in ["charging station", "EV charging", "Tata Power", "Jio bp", "Statiq", "Ather"]:
        resp = httpx.get(
            "https://nominatim.openstreetmap.org/search",
            params={
                "q": term,
                "viewbox": vb,
                "bounded": 1,
                "format": "jsonv2",
                "extratags": 1,
                "addressdetails": 1,
                "limit": 50,
            },
            headers=headers,
            timeout=15.0,
        )
        if resp.status_code == 200:
            for item in resp.json():
                if item.get("category") == "amenity" and item.get("type") == "charging_station":
                    ref = f"{item.get('osm_type')}/{item.get('osm_id')}"
                    nom_stations[ref] = item

print(f"Total genuine OSM amenity=charging_station POIs found via Nominatim: {len(nom_stations)}")
for ref, st in list(nom_stations.items())[:25]:
    print(f"  {ref}: {st.get('name') or 'Unnamed'} | ({st['lat']}, {st['lon']}) | tags={st.get('extratags')}")

# 3. Also test Overpass mirrors (CH / French / etc.)
print("\n=== Testing Overpass Interpreter for MP ===")
q = build_overpass_query(around_center=None, bbox=MP_BBOX)
for mirror in ["https://overpass.osm.ch/api/interpreter", "https://overpass-api.de/api/interpreter"]:
    try:
        r_ov = httpx.post(mirror, data={"data": q}, timeout=20.0)
        print(mirror, "->", r_ov.status_code, len(r_ov.text))
        if r_ov.status_code == 200 and r_ov.text.strip().startswith("{"):
            els = r_ov.json().get("elements", [])
            print("  Overpass MP charging stations:", len(els))
            Path("data/osm").mkdir(parents=True, exist_ok=True)
            Path("data/osm/mp_overpass_real.json").write_text(json.dumps(r_ov.json(), indent=2), encoding="utf-8")
            break
    except (httpx.HTTPError, ValueError, OSError) as exc:
        print(mirror, "-> ERR:", type(exc).__name__, exc)
