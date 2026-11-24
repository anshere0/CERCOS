"""Field research endpoints: mobile census audits, anonymous BWM surveys, and queuing observations."""
import csv
import io
from datetime import UTC, datetime
from typing import Any, Literal

from fastapi import APIRouter, HTTPException, Response, status

from app.schemas.field import (
    CensusRecord,
    QueueObservationCreate,
    SurveyResponseCreate,
)

router = APIRouter()

# In-memory storage stores for active session submissions and CSV export streaming
CENSUS_STORE: list[dict[str, Any]] = []
SURVEY_STORE: list[dict[str, Any]] = []
QUEUE_STORE: list[dict[str, Any]] = []


@router.post("/field/census", status_code=status.HTTP_201_CREATED)
def submit_census_record(record: CensusRecord) -> dict[str, Any]:
    """Ingest mobile hardware census audit for physical charging stations."""
    data = record.model_dump()
    data["audit_id"] = len(CENSUS_STORE) + 1
    data["submitted_at"] = datetime.now(UTC).isoformat()
    CENSUS_STORE.append(data)

    return {
        "status": "created",
        "audit_id": data["audit_id"],
        "station_name": data["station_name"],
        "source": "census",
        "confidence": 0.90,
    }


@router.post("/field/survey", status_code=status.HTTP_201_CREATED)
def submit_survey_response(response: SurveyResponseCreate) -> dict[str, Any]:
    """Submit anonymous driver BWM pairwise comparison responses.

    Strict informed consent gate: consent must be explicitly True or 422 is returned.
    Strict zero PII rule: absolutely no driver names, telephone numbers, or license plates.
    """
    if response.consent is not True:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Informed participant consent is strictly required (consent=True).",
        )

    data = response.model_dump()
    resp_id = len(SURVEY_STORE) + 1
    timestamp = datetime.now(UTC)
    data["response_id"] = resp_id
    data["collected_at"] = timestamp.isoformat()
    SURVEY_STORE.append(data)

    return {
        "status": "created",
        "response_id": resp_id,
        "collected_at": timestamp.isoformat(),
        "consent": True,
    }


@router.post("/field/queue", status_code=status.HTTP_201_CREATED)
def submit_queue_observation(observation: QueueObservationCreate) -> dict[str, Any]:
    """Submit 3-hour queuing observations ('07-10', '12-15', '18-21')."""
    data = observation.model_dump()
    obs_id = len(QUEUE_STORE) + 1
    data["obs_id"] = obs_id
    QUEUE_STORE.append(data)

    return {
        "status": "created",
        "obs_id": obs_id,
        "station_id": data["station_id"],
    }


@router.get("/field/export/{kind}")
def export_field_csv(
    kind: Literal["census", "survey", "queue"],
) -> Response:
    """Stream live CSV export of field data for census, survey, or queue records."""
    output = io.StringIO()

    if kind == "census":
        fields = ["audit_id", "station_name", "cpo_name", "latitude", "longitude", "max_power_kw", "tariff_inr_kwh", "is_operational", "submitted_at"]
        writer = csv.DictWriter(output, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        if CENSUS_STORE:
            for row in CENSUS_STORE:
                writer.writerow(row)
        else:
            # Output empty template row
            writer.writerow({
                "audit_id": 1,
                "station_name": "Ashta Sample Audit",
                "cpo_name": "Tata Power",
                "latitude": 23.0185,
                "longitude": 76.5342,
                "max_power_kw": 60.0,
                "tariff_inr_kwh": 18.5,
                "is_operational": True,
                "submitted_at": datetime.now(UTC).isoformat(),
            })

    elif kind == "survey":
        fields = ["response_id", "collected_at", "segment", "vehicle_model", "area", "range_anxiety", "best_criterion", "worst_criterion", "consent"]
        writer = csv.DictWriter(output, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        if SURVEY_STORE:
            for row in SURVEY_STORE:
                writer.writerow(row)
        else:
            writer.writerow({
                "response_id": 1,
                "collected_at": datetime.now(UTC).isoformat(),
                "segment": "E4W",
                "vehicle_model": "Tata Nexon EV",
                "area": "Bhopal",
                "range_anxiety": 4,
                "best_criterion": "cost",
                "worst_criterion": "wait",
                "consent": True,
            })

    elif kind == "queue":
        fields = ["obs_id", "station_id", "observed_at", "slot", "vehicles_waiting", "connectors_busy", "arrivals_in_interval", "interval_minutes"]
        writer = csv.DictWriter(output, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        if QUE_DATA := QUEUE_STORE:
            for row in QUE_DATA:
                writer.writerow(row)
        else:
            writer.writerow({
                "obs_id": 1,
                "station_id": 1,
                "observed_at": datetime.now(UTC).isoformat(),
                "slot": "12-15",
                "vehicles_waiting": 2,
                "connectors_busy": 2,
                "arrivals_in_interval": 4,
                "interval_minutes": 60,
            })
    else:
        raise HTTPException(status_code=400, detail="Invalid export kind. Expected census, survey, or queue.")

    csv_content = output.getvalue()
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={kind}_export.csv"},
    )
