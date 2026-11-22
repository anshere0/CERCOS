"""0001_initial from contracts/schema.sql

Revision ID: 0001_initial
Revises:
Create Date: 2026-11-22 19:30:00.000000

"""
from pathlib import Path
from typing import Sequence, Union

from alembic import op

revision: str = "0001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Execute contracts/schema.sql verbatim."""
    schema_paths = [
        Path("contracts/schema.sql"),
        Path(__file__).resolve().parents[3] / "contracts" / "schema.sql",
        Path(__file__).resolve().parents[2] / "contracts" / "schema.sql",
    ]
    sql_text = None
    for p in schema_paths:
        if p.exists():
            sql_text = p.read_text(encoding="utf-8")
            break

    if not sql_text:
        raise FileNotFoundError("contracts/schema.sql could not be found.")

    op.execute(sql_text)


def downgrade() -> None:
    """Drop cercos schema and all its objects."""
    op.execute("DROP SCHEMA IF EXISTS cercos CASCADE;")
