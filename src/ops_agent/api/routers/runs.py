"""Runs API router.

Endpoints:
- POST /runs: Start a workflow run
- GET /runs/{run_id}: Get run status and results
- POST /runs/{run_id}/events: Submit human feedback (Chapter 5+)
"""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request, status

from ops_agent.api.models import (
    IncidentCreate,
    RunCreateResponse,
    RunResponse,
    RunStateSnapshot,
    RunStatus,
)
from ops_agent.application.run_service import RunService

router = APIRouter(prefix="/runs", tags=["runs"])


def get_run_service(request: Request) -> RunService:
    """Dependency to get run service from app state."""
    return request.app.state.run_service


@router.post("", response_model=RunCreateResponse, status_code=status.HTTP_201_CREATED)
def create_run(incident: IncidentCreate, service: RunService = Depends(get_run_service)) -> RunCreateResponse:
    """Start a new workflow run for an incident.

    This endpoint:
    1. Creates a new run with a unique run_id
    2. Executes the workflow synchronously (Chapter 1)
    3. Returns the run_id and status

    In later chapters, this will return immediately and execution
    will happen asynchronously.
    """
    # Convert Pydantic model to dict
    incident_data = {
        "title": incident.title,
        "description": incident.description,
        "service": incident.service,
        "environment": incident.environment,
        "time_window": incident.time_window,
    }

    # Create and execute run
    run_id, trace_id = service.create_and_execute_run(incident_data)

    return RunCreateResponse(
        run_id=run_id,
        status="completed",  # In Chapter 1, execution is synchronous
        trace_id=trace_id,
    )


@router.get("/{run_id}", response_model=RunResponse)
def get_run(run_id: str, service: RunService = Depends(get_run_service)) -> RunResponse:
    """Get run status, state snapshot, and final result.

    Returns:
        - Run metadata (status, timestamps, trace_id)
        - Current state snapshot
        - Final structured output (IncidentActionPlan) if completed
    """
    run_data = service.get_run(run_id)

    if not run_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Run {run_id} not found",
        )

    # Extract state
    state = run_data.get("state", {})
    state_snapshot = RunStateSnapshot(
        incident=state.get("incident"),
        signals=state.get("signals", []),
        hypotheses=state.get("hypotheses", []),
        tool_results=state.get("tool_results", []),
        actions=state.get("actions", []),
        open_questions=state.get("open_questions", []),
        human_events=state.get("human_events", []),
        status=state.get("status", "unknown"),
    )

    return RunResponse(
        run=RunStatus(
            run_id=run_data["run_id"],
            status=run_data["status"],
            created_at=run_data["created_at"],
            updated_at=run_data["updated_at"],
            trace_id=run_data.get("trace_id"),
        ),
        state=state_snapshot,
        result=run_data.get("result"),  # Already a dict from IncidentActionPlan.to_dict()
    )


@router.post(
    "/{run_id}/events",
    response_model=RunResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
def submit_human_event(
    run_id: str,
    event: dict[str, Any],
    service: RunService = Depends(get_run_service),
) -> RunResponse:
    """Submit human feedback/approval/clarification and resume a run.

    This endpoint:
    1. Attaches the human event to the run state
    2. Re-executes the workflow to incorporate the feedback
    3. Returns the updated run status, state, and result
    """
    try:
        final_state = service.submit_human_event(run_id, event)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Run {run_id} not found",
        ) from None

    run_data = service.get_run(run_id)
    if not run_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Run {run_id} not found",
        )

    state_snapshot = RunStateSnapshot(
        incident=final_state.get("incident"),
        signals=final_state.get("signals", []),
        hypotheses=final_state.get("hypothesis", []),
        tool_results=final_state.get("tool_results", []),
        actions=final_state.get("actions", []),
        open_questions=final_state.get("open_questions", []),
        human_events=final_state.get("human_events", []),
        status=final_state.get("status", "unknown"),
    )

    return RunResponse(
        run=RunStatus(
            run_id=run_data["run_id"],
            status=run_data["status"],
            created_at=run_data["created_at"],
            updated_at=run_data["updated_at"],
            trace_id=run_data.get("trace_id"),
        ),
        state=state_snapshot,
        result=run_data.get("result"),
    )

