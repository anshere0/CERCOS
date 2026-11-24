"""Detailed multi-leg highway routing and turn-by-turn navigation via OSRM."""

from __future__ import annotations

import math
from typing import Any

import httpx
from fastapi import APIRouter
from pydantic import BaseModel

from app.schemas.recommend import LatLon

router = APIRouter()

OSRM_ROUTE_URL = "https://router.project-osrm.org/route/v1/driving"
_ROUTE_CACHE: dict[str, dict[str, Any]] = {}

# Real NH-46 Bhopal <-> Indore highway alignment fallback waypoints (lat, lon)
_NH46_ANCHORS: list[tuple[float, float, str]] = [
    (23.2599, 77.4126, "Bhopal City / Arera Hills"),
    (23.2686, 77.3385, "Bairagarh / NH-46 Junction"),
    (23.2286, 77.2005, "Phanda Toll Plaza (NH-46)"),
    (23.2147, 77.0783, "Sehore Bypass (NH-46)"),
    (23.0740, 76.8298, "Kothri Kalan / VIT Bhopal"),
    (23.0195, 76.7222, "Ashta Highway Interchange"),
    (23.0690, 76.4093, "Sonkatch Bridge (NH-46)"),
    (22.9780, 76.0520, "Dewas Industrial Bypass"),
    (22.7755, 75.9024, "Indore Dewas Naka Entry"),
    (22.7196, 75.8577, "Indore Central (Rajwada)"),
]


class RouteRequest(BaseModel):
    """Request body for multi-leg road routing with optional EV charging waypoint."""

    origin: LatLon
    destination: LatLon
    waypoint: LatLon | None = None
    waypoint_name: str | None = None


class RouteStep(BaseModel):
    """Single turn-by-turn driving maneuver along a route leg."""

    instruction: str
    road_name: str
    distance_m: float
    duration_s: float
    maneuver_type: str
    modifier: str | None = None
    location: list[float]  # [lat, lon]


class RouteLeg(BaseModel):
    """Continuous driving leg between origin/stop/destination."""

    from_label: str
    to_label: str
    distance_km: float
    duration_min: float
    coordinates: list[list[float]]  # [[lat, lon], ...]
    steps: list[RouteStep]


class RouteResponse(BaseModel):
    """Detailed highway route response with real street geometry and turn-by-turn steps."""

    provider: str
    total_distance_km: float
    total_duration_min: float
    legs: list[RouteLeg]


def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    r = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return r * 2 * math.asin(math.sqrt(min(1.0, max(0.0, a))))


def _bearing_cardinal(lat1: float, lon1: float, lat2: float, lon2: float) -> str:
    dlon = math.radians(lon2 - lon1)
    p1, p2 = math.radians(lat1), math.radians(lat2)
    y = math.sin(dlon) * math.cos(p2)
    x = math.cos(p1) * math.sin(p2) - math.sin(p1) * math.cos(p2) * math.cos(dlon)
    deg = (math.degrees(math.atan2(y, x)) + 360.0) % 360.0
    dirs = ["north", "northeast", "east", "southeast", "south", "southwest", "west", "northwest"]
    return dirs[int((deg + 22.5) // 45) % 8]


def _format_osrm_instruction(step: dict[str, Any], end_label: str) -> str:
    man = step.get("maneuver") or {}
    mtype = str(man.get("type") or "continue")
    mod = str(man.get("modifier") or "").strip()
    road = str(step.get("name") or "").strip()
    road_part = f" onto {road}" if road else ""

    if mtype == "depart":
        dir_txt = f" {mod}" if mod else ""
        on_txt = f" on {road}" if road else ""
        return f"Head{dir_txt}{on_txt}"
    if mtype == "arrive":
        return f"Arrive at {end_label}"
    if mtype in ("roundabout", "rotary"):
        exit_num = man.get("exit")
        exit_txt = f"take exit {exit_num}" if exit_num else "take the highway exit"
        return f"At the roundabout, {exit_txt}{road_part}"
    if mtype == "merge":
        return f"Merge {mod or 'forward'}{road_part}"
    if mtype in ("fork", "off ramp", "on ramp"):
        return f"Keep {mod or 'straight'}{road_part}"
    if mtype == "turn":
        return f"Turn {mod or 'ahead'}{road_part}"
    if mtype == "new name":
        return f"Continue{road_part}" if road else "Continue straight"
    return f"Continue {mod}{road_part}".strip() if mod else f"Follow road{road_part}"


def _build_fallback_leg(a: LatLon, b: LatLon, from_label: str, to_label: str) -> RouteLeg:
    """Build deterministic NH-46 corridor polyline fallback when OSRM is unreachable."""
    total_direct = _haversine_km(a.lat, a.lon, b.lat, b.lon)
    pts: list[tuple[float, float, str]] = [(a.lat, a.lon, from_label)]

    # Include intermediate NH-46 anchors between a and b longitude bounds
    lo_lon, hi_lon = min(a.lon, b.lon), max(a.lon, b.lon)
    candidates = [
        p for p in _NH46_ANCHORS
        if lo_lon + 0.03 <= p[1] <= hi_lon - 0.03
        and min(a.lat, b.lat) - 0.15 <= p[0] <= max(a.lat, b.lat) + 0.15
    ]
    candidates.sort(key=lambda p: _haversine_km(a.lat, a.lon, p[0], p[1]))
    for lat, lon, label in candidates:
        if _haversine_km(pts[-1][0], pts[-1][1], lat, lon) > 3.0:
            pts.append((lat, lon, label))
    pts.append((b.lat, b.lon, to_label))

    # Subdivide each span smoothly so map preview & polyline remain rich
    coords: list[list[float]] = []
    steps: list[RouteStep] = []
    total_km = 0.0
    for i in range(len(pts) - 1):
        lat1, lon1, _lbl1 = pts[i]
        lat2, lon2, lbl2 = pts[i + 1]
        seg_km = max(0.2, _haversine_km(lat1, lon1, lat2, lon2) * 1.15)
        total_km += seg_km
        n_sub = 8
        for k in range(n_sub):
            t = k / n_sub
            coords.append([round(lat1 + (lat2 - lat1) * t, 6), round(lon1 + (lon2 - lon1) * t, 6)])
        direction = _bearing_cardinal(lat1, lon1, lat2, lon2)
        steps.append(
            RouteStep(
                instruction=f"Drive {direction} toward {lbl2}" if i > 0 else f"Start {direction} on NH-46 toward {lbl2}",
                road_name="NH-46 / Regional Corridor",
                distance_m=round(seg_km * 1000.0, 1),
                duration_s=round((seg_km / 48.0) * 3600.0, 1),
                maneuver_type="depart" if i == 0 else "continue",
                modifier=direction,
                location=[round(lat1, 6), round(lon1, 6)],
            )
        )
    coords.append([round(b.lat, 6), round(b.lon, 6)])
    steps.append(
        RouteStep(
            instruction=f"Arrive at {to_label}",
            road_name="Destination",
            distance_m=0.0,
            duration_s=0.0,
            maneuver_type="arrive",
            modifier=None,
            location=[round(b.lat, 6), round(b.lon, 6)],
        )
    )
    est_km = round(max(total_km, total_direct * 1.18), 2)
    est_min = round((est_km / 48.0) * 60.0, 1)
    return RouteLeg(
        from_label=from_label,
        to_label=to_label,
        distance_km=est_km,
        duration_min=est_min,
        coordinates=coords,
        steps=steps,
    )


def _fetch_osrm_route(req: RouteRequest) -> RouteResponse:
    """Call public OSRM API for full road geometry and turn-by-turn steps."""
    points = [req.origin]
    labels = ["Origin"]
    if req.waypoint is not None:
        points.append(req.waypoint)
        labels.append(req.waypoint_name or "EV Charging Stop")
    points.append(req.destination)
    labels.append("Destination")

    coord_str = ";".join(f"{p.lon:.6f},{p.lat:.6f}" for p in points)
    url = f"{OSRM_ROUTE_URL}/{coord_str}"
    resp = httpx.get(
        url,
        params={"overview": "full", "geometries": "geojson", "steps": "true"},
        timeout=6.0,
    )
    resp.raise_for_status()
    payload = resp.json()
    if payload.get("code") != "Ok" or not payload.get("routes"):
        raise ValueError(f"OSRM non-Ok response: {payload.get('code')}")

    route_obj = payload["routes"][0]
    raw_legs = route_obj.get("legs") or []
    legs: list[RouteLeg] = []

    for idx, raw_leg in enumerate(raw_legs):
        end_lbl = labels[idx + 1] if idx + 1 < len(labels) else "Destination"
        start_lbl = labels[idx] if idx < len(labels) else "Origin"
        leg_coords: list[list[float]] = []
        parsed_steps: list[RouteStep] = []

        for step in raw_leg.get("steps") or []:
            geom_coords = (step.get("geometry") or {}).get("coordinates") or []
            for lon, lat in geom_coords:
                lat_lon = [round(float(lat), 6), round(float(lon), 6)]
                if not leg_coords or leg_coords[-1] != lat_lon:
                    leg_coords.append(lat_lon)

            man = step.get("maneuver") or {}
            loc = man.get("location") or [points[idx].lon, points[idx].lat]
            parsed_steps.append(
                RouteStep(
                    instruction=_format_osrm_instruction(step, end_lbl),
                    road_name=str(step.get("name") or "Corridor Road"),
                    distance_m=round(float(step.get("distance") or 0.0), 1),
                    duration_s=round(float(step.get("duration") or 0.0), 1),
                    maneuver_type=str(man.get("type") or "continue"),
                    modifier=man.get("modifier"),
                    location=[round(float(loc[1]), 6), round(float(loc[0]), 6)],
                )
            )

        if not leg_coords:
            leg_coords = [[points[idx].lat, points[idx].lon], [points[idx + 1].lat, points[idx + 1].lon]]

        legs.append(
            RouteLeg(
                from_label=start_lbl,
                to_label=end_lbl,
                distance_km=round(float(raw_leg.get("distance") or 0.0) / 1000.0, 2),
                duration_min=round(float(raw_leg.get("duration") or 0.0) / 60.0, 1),
                coordinates=leg_coords,
                steps=parsed_steps,
            )
        )

    return RouteResponse(
        provider="osrm",
        total_distance_km=round(float(route_obj.get("distance") or 0.0) / 1000.0, 2),
        total_duration_min=round(float(route_obj.get("duration") or 0.0) / 60.0, 1),
        legs=legs,
    )


@router.post("/route", response_model=RouteResponse)
def compute_detailed_route(request: RouteRequest) -> RouteResponse:
    """Return turn-by-turn road route geometry (OSRM live with NH-46 offline fallback)."""
    wp_key = f"{request.waypoint.lat:.5f},{request.waypoint.lon:.5f}" if request.waypoint else "none"
    cache_key = f"{request.origin.lat:.5f},{request.origin.lon:.5f}|{wp_key}|{request.destination.lat:.5f},{request.destination.lon:.5f}"

    cached = _ROUTE_CACHE.get(cache_key)
    if cached is not None:
        return RouteResponse(**cached)

    try:
        result = _fetch_osrm_route(request)
    except (httpx.HTTPError, ValueError, KeyError, OSError):
        if request.waypoint is not None:
            leg1 = _build_fallback_leg(request.origin, request.waypoint, "Origin", request.waypoint_name or "EV Charging Stop")
            leg2 = _build_fallback_leg(request.waypoint, request.destination, request.waypoint_name or "EV Charging Stop", "Destination")
            legs = [leg1, leg2]
        else:
            legs = [_build_fallback_leg(request.origin, request.destination, "Origin", "Destination")]

        result = RouteResponse(
            provider="nh46-corridor-fallback",
            total_distance_km=round(sum(leg.distance_km for leg in legs), 2),
            total_duration_min=round(sum(leg.duration_min for leg in legs), 1),
            legs=legs,
        )

    if len(_ROUTE_CACHE) >= 128:
        _ROUTE_CACHE.clear()
    _ROUTE_CACHE[cache_key] = result.model_dump()
    return result
