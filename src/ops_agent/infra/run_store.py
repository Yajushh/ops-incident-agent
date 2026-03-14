"""In-memory run store implementation.

This is a simple dict-based store for Chapter 1-3.
Chapter 7+ will add persistent storage (Postgres).
"""

from datetime import datetime
from typing import Any

from ops_agent.agentic.schemas import IncidentActionPlan
from ops_agent.agentic.state import RunState
from ops_agent.application.interfaces import RunStore


class InMemoryRunStore(RunStore):
    """In-memory implementation of RunStore using a dictionary.

    This is suitable for development and testing. For production,
    use a persistent implementation (PostgresRunStore).
    """

    def __init__(self) -> None:
        """Initialize empty store."""
        self._runs: dict[str, dict[str, Any]] = {}

    def create_run(
        self, run_id: str, trace_id: str | None, initial_state: RunState
    ) -> None:
        """Create a new run record."""
        now = datetime.utcnow()
        self._runs[run_id] = {
            "run_id": run_id,
            "trace_id": trace_id,
            "status": "running",
            "created_at": now,
            "updated_at": now,
            "state": initial_state,
            "result": None,
        }

    def get_run(self, run_id: str) -> dict[str, Any] | None:
        """Get run metadata and current state."""
        return self._runs.get(run_id)

    def update_run_state(self, run_id: str, state: RunState) -> None:
        """Update the state for a run."""
        if run_id not in self._runs:
            raise ValueError(f"Run {run_id} not found")

        self._runs[run_id]["state"] = state
        self._runs[run_id]["updated_at"] = datetime.utcnow()

    def update_run_status(
        self, run_id: str, status: str, result: IncidentActionPlan | None = None
    ) -> None:
        """Update run status and optionally final result."""
        if run_id not in self._runs:
            raise ValueError(f"Run {run_id} not found")

        self._runs[run_id]["status"] = status
        self._runs[run_id]["updated_at"] = datetime.utcnow()
        if result:
            self._runs[run_id]["result"] = result.to_dict()

