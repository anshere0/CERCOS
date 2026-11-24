"""Unit tests for district GeoJSON, VAHAN CSV, and field census loaders."""
from datetime import UTC, datetime

import pytest
from app.etl.census_import import parse_census_csv
from app.etl.districts_geojson import parse_districts_geojson
from app.etl.vahan_csv import parse_vahan_csv, parse_vahan_row


def test_districts_geojson_loader() -> None:
    """Verify GeoJSON FeatureCollection parsing, geometry standardization, and model EV city flagging."""
    geojson_data = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {"district_name": "Bhopal", "rto_code": "MP-04"},
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[[77.2, 23.1], [77.6, 23.1], [77.6, 23.5], [77.2, 23.5], [77.2, 23.1]]],
                },
            },
            {
                "type": "Feature",
                "properties": {"district_name": "Sehore", "rto_code": "MP-37"},
                "geometry": {
                    "type": "MultiPolygon",
                    "coordinates": [[[[76.8, 23.0], [77.1, 23.0], [77.1, 23.3], [76.8, 23.3], [76.8, 23.0]]]],
                },
            },
        ],
    }

    districts = parse_districts_geojson(geojson_data)
    assert len(districts) == 2

    # Bhopal is a Model EV City
    bhopal = next(d for d in districts if d["district_name"] == "Bhopal")
    assert bhopal["is_model_ev_city"] is True
    assert bhopal["rto_code"] == "MP-04"
    assert bhopal["geom"]["type"] == "MultiPolygon"
    assert bhopal["confidence"] == 0.95

    # Sehore is not a Model EV City
    sehore = next(d for d in districts if d["district_name"] == "Sehore")
    assert sehore["is_model_ev_city"] is False
    assert sehore["rto_code"] == "MP-37"


def test_vahan_csv_loader_valid() -> None:
    """Verify VAHAN 4.0 CSV vehicle registration parsing and total computation."""
    csv_data = """district_name,rto_code,ev_e2w,ev_e3w,ev_e4w,ev_other,ev_total,year
Bhopal,MP-04,18500,4200,3100,250,26050,2024
Indore,MP-09,32000,7500,5400,600,45500,2024
Sehore,MP-37,2100,650,220,30,3000,2024
"""
    records = parse_vahan_csv(csv_data)
    assert len(records) == 3

    bhopal = next(r for r in records if r["district_name"] == "Bhopal")
    assert bhopal["ev_total"] == 26050
    assert bhopal["ev_e2w"] == 18500
    assert bhopal["confidence"] == 0.95
    assert bhopal["source"] == "morth_vahan_4.0"


def test_vahan_csv_loader_negative_rejection() -> None:
    """Verify that negative registration numbers violate constraints and raise ValueError."""
    bad_row = {
        "district_name": "Dewas",
        "rto_code": "MP-41",
        "ev_e2w": "-15",  # Invalid negative count!
        "ev_e3w": "100",
        "ev_e4w": "50",
        "ev_other": "5",
    }
    with pytest.raises(ValueError, match="Non-negative constraint violated"):
        parse_vahan_row(bad_row, line_number=5)


def test_census_csv_loader_valid_and_rejects() -> None:
    """Verify ground truth census CSV ingestion with 0.90 confidence and reject tracking."""
    csv_data = """station_name,cpo_name,latitude,longitude,address,max_power_kw,tariff_inr_kwh,is_operational,open_24x7,connectors
Ashta Highway Express,Tata Power,23.0185,76.5342,NH 46 Highway,60.0,18.5,true,true,CCS2:60;Type2:22
Dewas Bypass Hub,Jio-bp pulse,22.9675,76.0534,Dewas Bypass,120.0,21.0,true,true,CCS2:120;CCS2:60
Malformed Station,Unknown,,,Missing Coords,,,,,
"""
    stations, rejects = parse_census_csv(csv_data, fetched_at=datetime.now(UTC))

    # 2 valid stations, 1 reject
    assert len(stations) == 2
    assert len(rejects) == 1

    ashta = stations[0]
    assert ashta["station_name"] == "Ashta Highway Express"
    assert ashta["confidence"] == 0.90
    assert ashta["max_power_kw"] == 60.0
    assert ashta["tariff_inr_kwh"] == 18.5
    assert len(ashta["connectors"]) == 2

    # Reject verification
    assert rejects[0]["job"] == "census_import"
    assert "Missing coordinates" in rejects[0]["reason"]
