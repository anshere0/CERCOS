"""Field research endpoints: persisted mobile census audits, BWM surveys, and queuing observations."""
import csv
import io
from datetime import UTC, datetime
from typing import Any, Literal

from fastapi import APIRouter, HTTPException, Response, status

from app.core.db import (
    fetch_field_rows,
    insert_field_census,
    insert_queue_observation,
    insert_survey_response,
)
from app.schemas.field import (
    CensusRecord,
    QueueObservationCreate,
    SurveyResponseCreate,
)

router = APIRouter()


@router.post("/field/census", status_code=status.HTTP_201_CREATED)
def submit_census_record(record: CensusRecord) -> dict[str, Any]:
    """Ingest and persist mobile hardware census audit for physical charging stations."""
    data = record.model_dump()
    data["submitted_at"] = datetime.now(UTC).isoformat()
    audit_id = insert_field_census(data)

    return {
        "status": "created",
        "id": audit_id,
        "audit_id": audit_id,
        "station_name": data["station_name"],
        "source": "census",
        "confidence": 0.90,
    }


@router.post("/field/survey", status_code=status.HTTP_201_CREATED)
def submit_survey_response(response: SurveyResponseCreate) -> dict[str, Any]:
    """Submit and persist anonymous driver BWM pairwise comparison responses.

    Strict informed consent gate: consent must be explicitly True or 422 is returned.
    Strict zero PII rule: absolutely no driver names, telephone numbers, or license plates.
    """
    if response.consent is not True:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Informed participant consent is strictly required (consent=True).",
        )

    data = response.model_dump()
    timestamp = datetime.now(UTC)
    data["collected_at"] = timestamp.isoformat()
    resp_id = insert_survey_response(data)

    return {
        "status": "created",
        "id": resp_id,
        "response_id": resp_id,
        "collected_at": timestamp.isoformat(),
        "consent": True,
    }


@router.post("/field/queue", status_code=status.HTTP_201_CREATED)
def submit_queue_observation(observation: QueueObservationCreate) -> dict[str, Any]:
    """Submit and persist 3-hour queuing observations ('07-10', '12-15', '18-21')."""
    data = observation.model_dump()
    obs_id = insert_queue_observation(data)

    return {
        "status": "created",
        "id": obs_id,
        "obs_id": obs_id,
        "station_id": data["station_id"],
    }


@router.get("/field/export/{kind}")
def export_field_csv(
    kind: Literal["census", "survey", "queue"],
) -> Response:
    """Stream live CSV export of persisted field data for census, survey, or queue records."""
    rows = fetch_field_rows(kind)
    output = io.StringIO()

    field_map = {
        "census": [
            "audit_id", "submitted_at", "station_name", "cpo_name",
            "latitude", "longitude", "max_power_kw", "tariff_inr_kwh", "is_operational",
        ],
        "survey": [
            "response_id", "collected_at", "segment", "vehicle_model",
            "area", "range_anxiety", "best_criterion", "worst_criterion", "consent",
        ],
        "queue": [
            "obs_id", "station_id", "observed_at", "slot",
            "vehicles_waiting", "connectors_busy", "arrivals_in_interval", "interval_minutes",
        ],
    }

    fields = field_map.get(kind)
    if not fields:
        raise HTTPException(status_code=400, detail="Invalid export kind. Expected census, survey, or queue.")

    writer = csv.DictWriter(output, fieldnames=fields, extrasaction="ignore")
    writer.writeheader()
    for r in rows:
        writer.writerow(r)

    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={kind}_export.csv"},
    )
