"""MoRTH VAHAN 4.0 district vehicle registration CSV normalization pipeline.

Ingests district registration counts, validates strict non-negative integer constraints,
and returns structured registration data for the Bhopal-Indore study corridor.
"""
import csv
import io
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


def parse_vahan_row(
    row: dict[str, Any],
    line_number: int = 0,
) -> dict[str, Any]:
    """Parse and validate a single MoRTH VAHAN CSV record.

    Enforces non-negative integer constraints on vehicle registrations.
    """
    clean_row = {k.strip().lower(): str(v).strip() for k, v in row.items() if k}

    district_name = (
        clean_row.get("district_name")
        or clean_row.get("district")
        or clean_row.get("rto")
    )
    if not district_name:
        raise ValueError(f"Line {line_number}: Missing district name in VAHAN record")

    name_clean = district_name.title()
    rto_code = clean_row.get("rto_code") or clean_row.get("rto")

    # Helper for non-negative integers
    def parse_non_negative_int(col: str) -> int:
        val_str = clean_row.get(col, "0")
        try:
            val = int(val_str) if val_str else 0
        except ValueError as err:
            raise ValueError(f"Line {line_number}: Invalid integer '{val_str}' for column {col}") from err
        if val < 0:
            raise ValueError(f"Line {line_number}: Non-negative constraint violated for {col}: {val} < 0")
        return val

    ev_e2w = parse_non_negative_int("ev_e2w")
    ev_e3w = parse_non_negative_int("ev_e3w")
    ev_e4w = parse_non_negative_int("ev_e4w")
    ev_other = parse_non_negative_int("ev_other")

    # If ev_total not explicitly given or less than sum, compute sum
    explicit_total = parse_non_negative_int("ev_total")
    computed_sum = ev_e2w + ev_e3w + ev_e4w + ev_other
    ev_total = max(explicit_total, computed_sum)

    # Year
    year_str = clean_row.get("ev_data_year") or clean_row.get("year", "2024")
    try:
        ev_data_year = int(year_str)
    except ValueError:
        ev_data_year = 2024

    return {
        "district_name": name_clean,
        "rto_code": rto_code,
        "ev_total": ev_total,
        "ev_e2w": ev_e2w,
        "ev_e3w": ev_e3w,
        "ev_e4w": ev_e4w,
        "ev_other": ev_other,
        "ev_data_year": ev_data_year,
        "source": "morth_vahan_4.0",
        "fetched_at": datetime.now(UTC),
        "confidence": 0.95,
    }


def parse_vahan_csv(
    csv_source: str | Path | io.StringIO,
) -> list[dict[str, Any]]:
    """Ingest VAHAN 4.0 district vehicle counts from a CSV file path, string, or stream."""
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

    records: list[dict[str, Any]] = []
    seen: dict[str, dict[str, Any]] = {}

    for idx, row in enumerate(reader, start=2):
        parsed = parse_vahan_row(row, line_number=idx)
        # Idempotent deduplication by district_name
        seen[parsed["district_name"]] = parsed

    records.extend(seen.values())
    return records
