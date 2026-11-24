"""Idempotent database seeder for offline development and testing.

Loads db/seeds/fixture_stations.json, validates against StationCreate Pydantic schema,
and provides a clean seeder callable for local databases or test harnesses.
"""
import json
from pathlib import Path
from typing import Any

from app.schemas.station import StationCreate


def load_fixture_stations(fixture_path: Path | None = None) -> list[dict[str, Any]]:
    """Load and validate the 20-station corridor seed dataset."""
    if fixture_path is None:
        possible_paths = [
            Path("db/seeds/fixture_stations.json"),
            Path("../db/seeds/fixture_stations.json"),
            Path(__file__).resolve().parents[2] / "fixture_stations.json",
        ]
        fixture_path = next((p for p in possible_paths if p.exists()), None)
        if fixture_path is None:
            raise FileNotFoundError("fixture_stations.json could not be found")

    content = json.loads(fixture_path.read_text(encoding="utf-8"))
    validated_stations: list[dict[str, Any]] = []

    for item in content:
        # Validate through Pydantic schema
        validated_obj = StationCreate(**item)
        validated_stations.append(validated_obj.model_dump())

    return validated_stations


def seed_database(session: Any = None, stations: list[dict[str, Any]] | None = None) -> int:
    """Seed charging stations into database idempotently.

    If session is None, returns the count of validated fixture stations ready for insertion.
    """
    station_data = stations or load_fixture_stations()

    if session is not None:
        from app.models.stations import ChargingStation, Connector

        count = 0
        for data in station_data:
            ref = data.get("source_ref")
            existing = session.query(ChargingStation).filter_by(source_ref=ref).first()
            if not existing:
                conns_data = data.pop("connectors", [])
                # Construct PostGIS Point
                lat = data.pop("latitude")
                lon = data.pop("longitude")
                geom_wkt = f"SRID=4326;POINT({lon} {lat})"

                station = ChargingStation(**data, geom=geom_wkt)
                session.add(station)
                session.flush()

                for c in conns_data:
                    conn = Connector(station_id=station.station_id, **c)
                    session.add(conn)
                count += 1
        session.commit()
        return count

    return len(station_data)


if __name__ == "__main__":
    stations = load_fixture_stations()
    print(f"Successfully loaded and validated {len(stations)} corridor fixture stations.")
