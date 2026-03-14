"""Request and response models for the API."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class IncidentCreate(BaseModel):
    """Request schema for creating a new incident."""

    title: str = Field(..., description="Short title of the incident")
    description: str = Field(..., description="Detailed description of the incident")
    service: str = Field(..., description="Affected service name")
    environment: str = Field(..., description="Environment (e.g., production, staging)")
    time_window: str = Field(
        ..., description="Time window when incident occurred (ISO format or relative)"
    )


class RunStatus(BaseModel):
    """Status of a workflow run."""

    run_id: str = Field(..., description="Unique identifier for the run")
    status: str = Field(..., description="Current status: pending, running, completed, failed, paused")
    created_at: datetime = Field(..., description="When the run was created")
    updated_at: datetime = Field(..., description="Last update timestamp")
    trace_id: str | None = Field(None, description="Trace ID for observability")


class RunStateSnapshot(BaseModel):
    """Snapshot of the workflow state at a point in time."""

    incident: dict[str, Any] | None = None
    signals: list[dict[str, Any]] = Field(default_factory=list)
    hypotheses: list[dict[str, Any]] = Field(default_factory=list)
    tool_results: list[dict[str, Any]] = Field(default_factory=list)
    actions: list[dict[str, Any]] = Field(default_factory=list)
    open_questions: list[str] = Field(default_factory=list)
    human_events: list[dict[str, Any]] = Field(default_factory=list)
    status: str = "pending"


class RunResponse(BaseModel):
    """Response for GET /runs/{run_id}."""

    run: RunStatus
    state: RunStateSnapshot | None = None
    result: dict[str, Any] | None = Field(
        None, description="Final structured output (IncidentActionPlan) if completed"
    )


class RunCreateResponse(BaseModel):
    """Response for POST /runs."""

    run_id: str
    status: str
    trace_id: str | None = None

