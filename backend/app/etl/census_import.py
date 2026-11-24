"""Field hardware census CSV audit import pipeline.

Ingests physical charging station audits collected by field researchers,
validates coordinates and connector ratings, and assigns high ground-truth confidence (0.90).
"""
import csv
import io
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

CENSUS_CONFIDENCE = 0.90


def parse_connectors_string(conn_str: str | None, max_power_fallback: float | None = None) -> list[dict[str, Any]]:
    """Parse connector string e.g. 'CCS2:60;Type2:22' or 'CCS2, Type2'."""
    connectors: list[dict[str, Any]] = []
    if not conn_str:
        return [{
            "connector_type": "Type2",
            "output_power_kw": max_power_fallback or 7.4,
            "status": "AVAILABLE",
        }]

    # Delimiters can be semicolons or commas
    parts = [p.strip() for p in conn_str.replace(",", ";").split(";") if p.strip()]
    for part in parts:
        if ":" in part:
            ctype, ckw = part.split(":", 1)
            try:
                kw_val = float(ckw.strip().replace("kW", "").replace("kw", ""))
            except ValueError:
                kw_val = max_power_fallback or 7.4
        else:
            ctype = part
            kw_val = max_power_fallback or 7.4

        connectors.append({
            "connector_type": ctype.strip(),
            "output_power_kw": kw_val,
            "status": "AVAILABLE",
        })

    return connectors


def parse_census_row(
    row: dict[str, Any],
    line_number: int = 0,
    fetched_at: datetime | None = None,
) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
    """Parse a single census CSV audit row into standardized station dict or reject record."""
    clean = {k.strip().lower(): str(v).strip() for k, v in row.items() if k}
    timestamp = fetched_at or datetime.now(UTC)

    station_name = clean.get("station_name") or clean.get("name")
    if not station_name:
        return None, {
            "job": "census_import",
            "raw": row,
            "reason": f"Line {line_number}: Missing station name in census audit",
            "created_at": timestamp,
        }

    # Coordinates
    lat_str = clean.get("latitude") or clean.get("lat")
    lon_str = clean.get("longitude") or clean.get("lon")

    if not lat_str or not lon_str:
        return None, {
            "job": "census_import",
            "raw": row,
            "reason": f"Line {line_number}: Missing coordinates for station '{station_name}'",
            "created_at": timestamp,
        }

    try:
        lat = float(lat_str)
        lon = float(lon_str)
    except ValueError:
        return None, {
            "job": "census_import",
            "raw": row,
            "reason": f"Line {line_number}: Malformed coordinates ({lat_str}, {lon_str})",
            "created_at": timestamp,
        }

    if not (-90.0 <= lat <= 90.0 and -180.0 <= lon <= 180.0):
        return None, {
            "job": "census_import",
            "raw": row,
            "reason": f"Line {line_number}: Coordinates out of range ({lat}, {lon})",
            "created_at": timestamp,
        }

    # Max power & tariff
    max_power_kw: float | None = None
    if clean.get("max_power_kw"):
        try:
            max_power_kw = float(clean["max_power_kw"])
        except ValueError:
            pass

    tariff: float | None = None
    if clean.get("tariff_inr_kwh"):
        try:
            tariff = float(clean["tariff_inr_kwh"])
        except ValueError:
            pass

    rating: float | None = None
    if clean.get("rating"):
        try:
            rating = float(clean["rating"])
        except ValueError:
            pass

    is_operational = clean.get("is_operational", "true").lower() in ("true", "1", "yes")
    open_24x7 = clean.get("open_24x7", "true").lower() in ("true", "1", "yes")

    connectors = parse_connectors_string(clean.get("connectors"), max_power_fallback=max_power_kw)
    if not max_power_kw and connectors:
        max_power_kw = max(c["output_power_kw"] for c in connectors)

    station_data = {
        "station_name": station_name,
        "cpo_name": clean.get("cpo_name") or clean.get("operator"),
        "address": clean.get("address"),
        "max_power_kw": max_power_kw,
        "tariff_inr_kwh": tariff,
        "rating": rating,
        "is_operational": is_operational,
        "open_24x7": open_24x7,
        "hours_text": clean.get("hours_text", "24/7" if open_24x7 else None),
        "contact": clean.get("contact"),
        "latitude": lat,
        "longitude": lon,
        "source": "census",
        "source_ref": f"census:{clean.get('audit_id') or station_name.lower().replace(' ', '_')}",
        "fetched_at": timestamp,
        "confidence": CENSUS_CONFIDENCE,
        "connectors": connectors,
    }

    return station_data, None


def parse_census_csv(
    csv_source: str | Path | io.StringIO,
    fetched_at: datetime | None = None,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Parse field census audits from CSV file or string into valid stations and rejects."""
    if isinstance(csv_source, Path):
        reader = csv.DictReader(csv_source.open(mode="r", encoding="utf-8"))
    elif isinstance(csv_source, str):
        if "\n" in csv_source or "\r" in csv_source:
            reader = csv.DictReader(io.StringIO(csv_source))
        else:
            try:
                p = Path(csv_source)
                if p.exists() and p.is_file():
                    reader = csv.DictReader(p.open(mode="r", encoding="utf-8"))
                else:
                    reader = csv.DictReader(io.StringIO(csv_source))
            except (OSError, ValueError):
                reader = csv.DictReader(io.StringIO(csv_source))
    else:
        reader = csv.DictReader(csv_source)

    valid_stations: list[dict[str, Any]] = []
    rejects: list[dict[str, Any]] = []

    seen_refs: set[str] = set()

    for idx, row in enumerate(reader, start=2):
        station, reject = parse_census_row(row, line_number=idx, fetched_at=fetched_at)
        if reject:
            rejects.append(reject)
        elif station:
            ref = station["source_ref"]
            if ref not in seen_refs:
                seen_refs.add(ref)
                valid_stations.append(station)

    return valid_stations, rejects
