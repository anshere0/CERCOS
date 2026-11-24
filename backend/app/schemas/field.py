"""Pydantic v2 schemas for field census, anonymous surveys, and queuing observations."""
from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class CensusRecord(BaseModel):
    """Field audit ingestion schema for physical charging station audits."""
    station_name: str
    cpo_name: str | None = None
    latitude: float = Field(..., ge=-90.0, le=90.0)
    longitude: float = Field(..., ge=-180.0, le=180.0)
    address: str | None = None
    max_power_kw: float | None = None
    tariff_inr_kwh: float | None = None
    is_operational: bool = True
    open_24x7: bool = True
    connector_types: list[str] = []
    photo_url: str | None = None
    auditor: str | None = None


class SurveyResponseCreate(BaseModel):
    """Driver BWM survey response creation schema.

    Strict zero PII rule: absolutely no driver names, telephone numbers, or license plates.
    Consent must be strictly True or validation fails immediately.
    """
    model_config = ConfigDict(extra="forbid")

    segment: Literal["E2W", "E3W", "E4W", "ELCV"]
    vehicle_model: str | None = None
    area: str | None = None
    home_charging: bool | None = None
    range_anxiety: int | None = Field(None, ge=1, le=5)
    best_criterion: str
    worst_criterion: str
    best_to_others: dict[str, Any]
    others_to_worst: dict[str, Any]
    wtp_zero_wait_inr: float | None = None
    consent: bool = Field(...)
    enumerator: str | None = None

    @field_validator("consent")
    @classmethod
    def validate_consent(cls, v: bool) -> bool:
        if v is not True:
            raise ValueError("Participant informed consent is strictly required (consent=True).")
        return v


class SurveyResponseRead(BaseModel):
    """Schema for reading survey responses with ID and timestamp."""
    model_config = ConfigDict(from_attributes=True)
    response_id: int
    collected_at: datetime
    segment: str
    vehicle_model: str | None = None
    area: str | None = None
    home_charging: bool | None = None
    range_anxiety: int | None = None
    best_criterion: str
    worst_criterion: str
    best_to_others: dict[str, Any]
    others_to_worst: dict[str, Any]
    wtp_zero_wait_inr: float | None = None
    consent: bool
    enumerator: str | None = None


class QueueObservationCreate(BaseModel):
    """Schema for submitting 3-hour queuing observations."""
    station_id: int
    observed_at: datetime
    slot: Literal["07-10", "12-15", "18-21"] | None = None
    vehicles_waiting: int | None = Field(None, ge=0)
    connectors_busy: int | None = Field(None, ge=0)
    arrivals_in_interval: int | None = Field(None, ge=0)
    interval_minutes: int | None = Field(None, ge=1)
    session_start: datetime | None = None
    session_end: datetime | None = None
    kwh_delivered: float | None = Field(None, ge=0)
    observer: str | None = None


class QueueObservationRead(QueueObservationCreate):
    """Schema for reading queue observations with observation ID."""
    model_config = ConfigDict(from_attributes=True)
    obs_id: int
