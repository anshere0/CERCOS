"""Database connectivity, auto-detection (PostgreSQL/PostGIS vs SQLite persistence), and seeding layer."""
import json
import sqlite3
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError

from app.core.config import settings

_REPO_ROOT = Path(__file__).resolve().parents[3]
_SQLITE_DB_PATH = _REPO_ROOT / "data" / "cercos_local.db"

_DB_BACKEND: str | None = None
_ENGINE: Engine | None = None


def _get_sqlite_conn() -> sqlite3.Connection:
    """Return a configured SQLite connection with Row factory and ensured schema."""
    _SQLITE_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(_SQLITE_DB_PATH), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    _ensure_sqlite_schema(conn)
    return conn


def _ensure_sqlite_schema(conn: sqlite3.Connection) -> None:
    """Create relational tables in local SQLite mirroring contracts/schema.sql."""
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS charging_stations (
            station_id INTEGER PRIMARY KEY AUTOINCREMENT,
            cpo_name TEXT,
            station_name TEXT NOT NULL,
            address TEXT,
            latitude REAL NOT NULL,
            longitude REAL NOT NULL,
            max_power_kw REAL,
            tariff_inr_kwh REAL,
            rating REAL,
            is_operational INTEGER DEFAULT 1,
            open_24x7 INTEGER DEFAULT 1,
            hours_text TEXT,
            contact TEXT,
            source TEXT NOT NULL,
            source_ref TEXT UNIQUE,
            fetched_at TEXT NOT NULL,
            confidence REAL NOT NULL,
            connectors_json TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS survey_responses (
            response_id INTEGER PRIMARY KEY AUTOINCREMENT,
            collected_at TEXT NOT NULL,
            segment TEXT NOT NULL,
            vehicle_model TEXT,
            area TEXT,
            home_charging INTEGER,
            range_anxiety INTEGER,
            best_criterion TEXT NOT NULL,
            worst_criterion TEXT NOT NULL,
            best_to_others_json TEXT NOT NULL,
            others_to_worst_json TEXT NOT NULL,
            wtp_zero_wait_inr REAL,
            consent INTEGER NOT NULL CHECK (consent = 1),
            enumerator TEXT
        );

        CREATE TABLE IF NOT EXISTS census_audits (
            audit_id INTEGER PRIMARY KEY AUTOINCREMENT,
            submitted_at TEXT NOT NULL,
            station_name TEXT NOT NULL,
            cpo_name TEXT,
            latitude REAL NOT NULL,
            longitude REAL NOT NULL,
            address TEXT,
            max_power_kw REAL,
            tariff_inr_kwh REAL,
            is_operational INTEGER DEFAULT 1,
            open_24x7 INTEGER DEFAULT 1,
            connector_types_json TEXT,
            enumerator TEXT
        );

        CREATE TABLE IF NOT EXISTS station_observations (
            obs_id INTEGER PRIMARY KEY AUTOINCREMENT,
            station_id INTEGER NOT NULL,
            observed_at TEXT NOT NULL,
            slot TEXT,
            vehicles_waiting INTEGER,
            connectors_busy INTEGER,
            arrivals_in_interval INTEGER,
            interval_minutes INTEGER,
            observer TEXT
        );

        CREATE TABLE IF NOT EXISTS recommendations_log (
            rec_id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT NOT NULL,
            request_json TEXT NOT NULL,
            response_json TEXT NOT NULL,
            mode TEXT NOT NULL,
            engine_version TEXT NOT NULL
        );
        """
    )
    conn.commit()


def _seed_sqlite_if_empty(conn: sqlite3.Connection) -> None:
    """Populate SQLite charging_stations from real OSM data + corridor verified stations idempotently."""
    cur = conn.execute("SELECT COUNT(*) FROM charging_stations")
    if cur.fetchone()[0] > 0:
        return

    real_osm_file = _REPO_ROOT / "data" / "osm" / "mp_corridor_real_stations.json"
    fixture_file = _REPO_ROOT / "db" / "seeds" / "fixture_stations.json"

    stations_to_load: list[dict[str, Any]] = []
    if real_osm_file.exists():
        stations_to_load.extend(json.loads(real_osm_file.read_text(encoding="utf-8")))
    elif fixture_file.exists():
        stations_to_load.extend(json.loads(fixture_file.read_text(encoding="utf-8")))

    now_iso = datetime.now(UTC).isoformat()
    for idx, s in enumerate(stations_to_load, start=1):
        ref = s.get("source_ref") or f"seed:station_{idx}"
        conn.execute(
            """
            INSERT OR IGNORE INTO charging_stations (
                cpo_name, station_name, address, latitude, longitude,
                max_power_kw, tariff_inr_kwh, rating, is_operational,
                open_24x7, hours_text, contact, source, source_ref,
                fetched_at, confidence, connectors_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                s.get("cpo_name"),
                s["station_name"],
                s.get("address"),
                float(s["latitude"]),
                float(s["longitude"]),
                float(s["max_power_kw"]) if s.get("max_power_kw") is not None else None,
                float(s["tariff_inr_kwh"]) if s.get("tariff_inr_kwh") is not None else None,
                float(s["rating"]) if s.get("rating") is not None else None,
                1 if s.get("is_operational", True) else 0,
                1 if s.get("open_24x7", True) else 0,
                s.get("hours_text"),
                s.get("contact"),
                s.get("source", "osm"),
                ref,
                str(s.get("fetched_at") or now_iso),
                float(s.get("confidence", 0.90)),
                json.dumps(s.get("connectors", [])),
            ),
        )
    conn.commit()


def check_database_status() -> dict[str, Any]:
    """Probe PostgreSQL first; cleanly report active database dialect and station count."""
    global _DB_BACKEND, _ENGINE
    pg_url = settings.DATABASE_URL
    # Try PostgreSQL only when psycopg / psycopg2 driver is usable
    try:
        pg_engine = create_engine(pg_url, pool_pre_ping=True, connect_args={"connect_timeout": 2})
        with pg_engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            res = conn.execute(text("SELECT COUNT(*) FROM cercos.charging_stations")).scalar()
        _DB_BACKEND = "postgresql+postgis"
        _ENGINE = pg_engine
        return {"backend": "postgresql+postgis", "connected": True, "stations_count": int(res or 0)}
    except (SQLAlchemyError, OSError, ModuleNotFoundError, ImportError) as pg_err:
        # Local persistent SQLite fallback when Postgres server isn't started
        try:
            sq = _get_sqlite_conn()
            _seed_sqlite_if_empty(sq)
            cnt = sq.execute("SELECT COUNT(*) FROM charging_stations").fetchone()[0]
            sq.close()
            _DB_BACKEND = "sqlite"
            return {
                "backend": "sqlite",
                "connected": True,
                "stations_count": int(cnt),
                "postgres_note": f"Postgres unavailable locally ({type(pg_err).__name__}); using persistent SQLite store",
            }
        except (sqlite3.Error, OSError) as sq_err:
            return {"backend": "none", "connected": False, "error": str(sq_err)}


def fetch_stations_from_db(source: str | None = None) -> list[dict[str, Any]]:
    """Read charging stations from PostgreSQL/PostGIS if live, else from seeded SQLite."""
    status = check_database_status()
    if status.get("backend") == "postgresql+postgis" and _ENGINE is not None:
        with _ENGINE.connect() as conn:
            sql = """
                SELECT s.station_id, s.cpo_name, s.station_name, s.address,
                       ST_Y(s.geom) AS latitude, ST_X(s.geom) AS longitude,
                       s.max_power_kw, s.tariff_inr_kwh, s.rating,
                       s.is_operational, s.open_24x7, s.hours_text, s.contact,
                       s.source, s.source_ref, s.fetched_at, s.confidence
                FROM cercos.charging_stations s
                ORDER BY s.station_id
            """
            rows = conn.execute(text(sql)).mappings().all()
            stations: list[dict[str, Any]] = []
            for r in rows:
                st = dict(r)
                if source and st.get("source") != source:
                    continue
                conns_rows = conn.execute(
                    text("SELECT connector_id, station_id, connector_type, output_power_kw, status FROM cercos.connectors WHERE station_id = :sid"),
                    {"sid": st["station_id"]},
                ).mappings().all()
                st["connectors"] = [
                    {
                        "connector_id": c["connector_id"],
                        "station_id": c["station_id"],
                        "connector_type": c["connector_type"],
                        "output_power_kw": float(c["output_power_kw"]),
                        "status": c["status"],
                    }
                    for c in conns_rows
                ]
                for num_k in ("max_power_kw", "tariff_inr_kwh", "rating", "confidence", "latitude", "longitude"):
                    if st.get(num_k) is not None:
                        st[num_k] = float(st[num_k])
                stations.append(st)
            if stations:
                return stations

    # Local persistent SQLite path
    sq = _get_sqlite_conn()
    _seed_sqlite_if_empty(sq)
    try:
        rows = sq.execute("SELECT * FROM charging_stations ORDER BY station_id").fetchall()
        results: list[dict[str, Any]] = []
        for r in rows:
            if source and r["source"] != source:
                continue
            conns = json.loads(r["connectors_json"] or "[]")
            formatted_conns = [
                {
                    "connector_id": r["station_id"] * 100 + idx,
                    "station_id": r["station_id"],
                    "connector_type": c.get("connector_type", "Type2"),
                    "output_power_kw": float(c.get("output_power_kw", 7.4)),
                    "status": c.get("status", "AVAILABLE"),
                }
                for idx, c in enumerate(conns, start=1)
            ]
            results.append(
                {
                    "station_id": int(r["station_id"]),
                    "cpo_name": r["cpo_name"],
                    "station_name": r["station_name"],
                    "address": r["address"],
                    "latitude": float(r["latitude"]),
                    "longitude": float(r["longitude"]),
                    "max_power_kw": float(r["max_power_kw"]) if r["max_power_kw"] is not None else None,
                    "tariff_inr_kwh": float(r["tariff_inr_kwh"]) if r["tariff_inr_kwh"] is not None else None,
                    "rating": float(r["rating"]) if r["rating"] is not None else None,
                    "is_operational": bool(r["is_operational"]),
                    "open_24x7": bool(r["open_24x7"]),
                    "hours_text": r["hours_text"],
                    "contact": r["contact"],
                    "source": r["source"],
                    "source_ref": r["source_ref"],
                    "fetched_at": r["fetched_at"],
                    "confidence": float(r["confidence"]),
                    "connectors": formatted_conns,
                }
            )
        return results
    finally:
        sq.close()


def insert_field_census(data: dict[str, Any]) -> int:
    """Persist field census record and register station in persistent store."""
    sq = _get_sqlite_conn()
    try:
        cur = sq.execute(
            """
            INSERT INTO census_audits (
                submitted_at, station_name, cpo_name, latitude, longitude,
                address, max_power_kw, tariff_inr_kwh, is_operational,
                open_24x7, connector_types_json, enumerator
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                data["submitted_at"],
                data["station_name"],
                data.get("cpo_name"),
                float(data["latitude"]),
                float(data["longitude"]),
                data.get("address"),
                float(data.get("max_power_kw") or 22.0),
                float(data.get("tariff_inr_kwh") or 16.0),
                1 if data.get("is_operational", True) else 0,
                1 if data.get("open_24x7", True) else 0,
                json.dumps(data.get("connector_types", ["Type2"])),
                data.get("enumerator"),
            ),
        )
        sq.commit()
        return int(cur.lastrowid)
    finally:
        sq.close()


def insert_survey_response(data: dict[str, Any]) -> int:
    """Persist consented anonymized BWM survey response."""
    sq = _get_sqlite_conn()
    try:
        cur = sq.execute(
            """
            INSERT INTO survey_responses (
                collected_at, segment, vehicle_model, area, home_charging,
                range_anxiety, best_criterion, worst_criterion,
                best_to_others_json, others_to_worst_json,
                wtp_zero_wait_inr, consent, enumerator
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                data["collected_at"],
                data["segment"],
                data.get("vehicle_model"),
                data.get("area"),
                1 if data.get("home_charging") else 0,
                data.get("range_anxiety"),
                data["best_criterion"],
                data["worst_criterion"],
                json.dumps(data.get("best_to_others", {})),
                json.dumps(data.get("others_to_worst", {})),
                data.get("wtp_zero_wait_inr"),
                1 if data.get("consent") else 0,
                data.get("enumerator"),
            ),
        )
        sq.commit()
        return int(cur.lastrowid)
    finally:
        sq.close()


def insert_queue_observation(data: dict[str, Any]) -> int:
    """Persist station queue observation interval."""
    sq = _get_sqlite_conn()
    try:
        cur = sq.execute(
            """
            INSERT INTO station_observations (
                station_id, observed_at, slot, vehicles_waiting,
                connectors_busy, arrivals_in_interval, interval_minutes, observer
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                int(data["station_id"]),
                str(data.get("observed_at") or datetime.now(UTC).isoformat()),
                data.get("slot"),
                data.get("vehicles_waiting"),
                data.get("connectors_busy"),
                data.get("arrivals_in_interval"),
                data.get("interval_minutes"),
                data.get("observer"),
            ),
        )
        sq.commit()
        return int(cur.lastrowid)
    finally:
        sq.close()


def fetch_field_rows(kind: str) -> list[dict[str, Any]]:
    """Retrieve persisted field records for CSV export."""
    sq = _get_sqlite_conn()
    try:
        table_map = {
            "census": "census_audits",
            "survey": "survey_responses",
            "queue": "station_observations",
        }
        table = table_map.get(kind)
        if not table:
            return []
        rows = sq.execute(f"SELECT * FROM {table} ORDER BY 1").fetchall()
        return [dict(r) for r in rows]
    finally:
        sq.close()


def log_recommendation(request_data: dict[str, Any], response_data: dict[str, Any], mode: str, engine_version: str) -> None:
    """Audit recommendation input/output into recommendations_log."""
    sq = _get_sqlite_conn()
    try:
        sq.execute(
            """
            INSERT INTO recommendations_log (created_at, request_json, response_json, mode, engine_version)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                datetime.now(UTC).isoformat(),
                json.dumps(request_data, default=str),
                json.dumps(response_data, default=str),
                mode,
                engine_version,
            ),
        )
        sq.commit()
    finally:
        sq.close()
