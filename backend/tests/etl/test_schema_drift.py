"""Automated schema drift detection and model smoke tests.

Validates that SQLAlchemy 2.0 ORM models match contracts/schema.sql with zero drift.
"""
import re
from pathlib import Path

import pytest
from app.models import Base
from app.schemas.field import SurveyResponseCreate
from app.schemas.station import StationCreate
from pydantic import ValidationError


def strip_sql_comments(text: str) -> str:
    """Remove line and block comments from SQL text."""
    # Remove single line comments
    text = re.sub(r"--[^\n]*", "", text)
    # Remove block comments
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.DOTALL)
    return text


def split_sql_statements(body: str) -> list[str]:
    """Split column and constraint definitions by commas outside parentheses."""
    tokens: list[str] = []
    current: list[str] = []
    paren_depth = 0
    for char in body:
        if char == "(":
            paren_depth += 1
            current.append(char)
        elif char == ")":
            paren_depth -= 1
            current.append(char)
        elif char == "," and paren_depth == 0:
            tokens.append("".join(current).strip())
            current = []
        else:
            current.append(char)
    if current:
        tokens.append("".join(current).strip())
    return tokens


def parse_contract_tables_and_columns(sql_path: Path) -> dict[str, set[str]]:
    """Parse table names and column names from contracts/schema.sql."""
    content = sql_path.read_text(encoding="utf-8")
    table_pattern = re.compile(
        r"CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?cercos\.(\w+)\s*\((.*?)\);",
        re.DOTALL | re.IGNORECASE,
    )

    tables: dict[str, set[str]] = {}
    for match in table_pattern.finditer(content):
        table_name = match.group(1).lower()
        body = strip_sql_comments(match.group(2))
        raw_statements = split_sql_statements(body)
        columns: set[str] = set()

        for raw_stmt in raw_statements:
            clean_stmt = raw_stmt.strip()
            if not clean_stmt:
                continue

            if re.match(r"^(PRIMARY\s+KEY|FOREIGN\s+KEY|CONSTRAINT|CHECK)\b", clean_stmt, re.IGNORECASE):
                continue

            # In SQL, multiple column definitions might be on one line separated by whitespace or commas,
            # but split_sql_statements handled top-level commas. Handle sublines if any:
            sub_lines = clean_stmt.split("\n")
            for sub_line in sub_lines:
                line_str = sub_line.strip()
                if not line_str or re.match(r"^(PRIMARY\s+KEY|FOREIGN\s+KEY|CONSTRAINT|CHECK)\b", line_str, re.IGNORECASE):
                    continue
                words = line_str.split()
                if words:
                    candidate = words[0].lower().strip('"')
                    if re.match(r"^[a-z_][a-z0-9_]*$", candidate):
                        columns.add(candidate)

        tables[table_name] = columns

    return tables


def test_schema_drift_tables_and_columns() -> None:
    """Ensure all tables and columns in contracts/schema.sql match SQLAlchemy metadata."""
    possible_paths = [
        Path("contracts/schema.sql"),
        Path("../contracts/schema.sql"),
        Path(__file__).resolve().parents[3] / "contracts" / "schema.sql",
    ]
    sql_file = next((p for p in possible_paths if p.exists()), None)
    assert sql_file is not None, "contracts/schema.sql could not be found"

    contract_tables = parse_contract_tables_and_columns(sql_file)
    assert len(contract_tables) == 8, f"Expected 8 tables in contract, parsed {len(contract_tables)}"

    # Check against SQLAlchemy metadata
    metadata_tables = {
        table.name: {col.name for col in table.columns}
        for table in Base.metadata.tables.values()
    }

    # Verify table existence
    for table_name in contract_tables:
        assert table_name in metadata_tables, f"Table {table_name} missing from SQLAlchemy metadata"

    for table_name, expected_cols in contract_tables.items():
        actual_cols = metadata_tables[table_name]
        missing_cols = expected_cols - actual_cols
        assert not missing_cols, f"Table {table_name} missing columns: {missing_cols}"
        extra_cols = actual_cols - expected_cols
        assert not extra_cols, f"Table {table_name} has unexpected extra columns: {extra_cols}"


def test_survey_schema_consent_enforcement() -> None:
    """Ensure SurveyResponseCreate strictly enforces consent=True and rejects consent=False."""
    valid_payload = {
        "segment": "E4W",
        "best_criterion": "cost",
        "worst_criterion": "wait",
        "best_to_others": {"cost": 1, "wait": 5},
        "others_to_worst": {"wait": 1, "cost": 5},
        "consent": True,
    }
    # Valid submission succeeds
    survey = SurveyResponseCreate(**valid_payload)
    assert survey.consent is True

    # Consent=False must raise ValidationError
    invalid_payload = valid_payload.copy()
    invalid_payload["consent"] = False
    with pytest.raises(ValidationError):
        SurveyResponseCreate(**invalid_payload)

    # Missing consent must raise ValidationError
    missing_consent = valid_payload.copy()
    del missing_consent["consent"]
    with pytest.raises(ValidationError):
        SurveyResponseCreate(**missing_consent)

    # Extra PII field must raise ValidationError (extra="forbid")
    pii_payload = valid_payload.copy()
    pii_payload["driver_name"] = "John Doe"
    with pytest.raises(ValidationError):
        SurveyResponseCreate(**pii_payload)


def test_station_schema_provenance_validation() -> None:
    """Ensure StationCreate requires source and confidence within [0, 1]."""
    valid_station = {
        "station_name": "Bhopal Junction EV Hub",
        "latitude": 23.2599,
        "longitude": 77.4126,
        "source": "osm",
        "confidence": 0.85,
    }
    station = StationCreate(**valid_station)
    assert station.source == "osm"
    assert station.confidence == 0.85

    # Missing source
    no_source = valid_station.copy()
    del no_source["source"]
    with pytest.raises(ValidationError):
        StationCreate(**no_source)

    # Missing confidence
    no_conf = valid_station.copy()
    del no_conf["confidence"]
    with pytest.raises(ValidationError):
        StationCreate(**no_conf)

    # Invalid confidence > 1.0
    bad_conf = valid_station.copy()
    bad_conf["confidence"] = 1.5
    with pytest.raises(ValidationError):
        StationCreate(**bad_conf)
