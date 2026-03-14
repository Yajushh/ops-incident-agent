"""Service for managing workflow runs.

This service orchestrates:
- Creating runs
- Executing workflows
- Storing run state
- Retrieving run status and results
"""

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Tuple

import structlog

from ops_agent.agentic.state import RunState
from ops_agent.application.executor import SyncWorkflowExecutor
from ops_agent.application.interfaces import RunStore

logger = structlog.get_logger(__name__)


class RunService:
    """Service for managing incident response workflow runs."""

    def __init__(self, executor: SyncWorkflowExecutor, run_store: RunStore) -> None:
        """Initialize service.

        Args:
            executor: Workflow executor
            run_store: Run storage
        """
        self.executor = executor
        self.run_store = run_store

    def create_and_execute_run(
        self, incident_data: Dict[str, str]
    ) -> Tuple[str, str | None]:
        """Create a new run and execute it synchronously.

        Args:
            incident_data: Incident data from API request

        Returns:
            Tuple of (run_id, trace_id)
        """
        run_id = str(uuid.uuid4())
        trace_id = f"trace_{run_id[:8]}"

        logger.info("creating_run", run_id=run_id, trace_id=trace_id)

        # Build initial state
        initial_state: RunState = {
            "incident": incident_data,
            "signals": [],
            "hypotheses": [],
            "tool_results": [],
            "actions": [],
            "open_questions": [],
            "human_events": [],
            "status": "running",
            "result": None,
            "trace_id": trace_id,
        }

        # Store run
        self.run_store.create_run(run_id, trace_id, initial_state)

        # Execute workflow
        try:
            final_state, result = self.executor.execute(run_id, initial_state)

            # Update run with final state
            self.run_store.update_run_state(run_id, final_state)
            if result:
                self.run_store.update_run_status(run_id, "completed", result)
            else:
                self.run_store.update_run_status(run_id, final_state.get("status", "failed"))

            logger.info(
                "run_completed",
                run_id=run_id,
                trace_id=trace_id,
                status=final_state.get("status"),
            )

        except Exception as e:
            logger.error(
                "run_execution_failed",
                run_id=run_id,
                trace_id=trace_id,
                error=str(e),
                exc_info=True,
            )
            self.run_store.update_run_status(run_id, "failed")

        return run_id, trace_id

    def submit_human_event(self, run_id: str, event: Dict[str, Any]) -> RunState:
        """Attach a human event to a run and optionally resume execution.

        This is the main entry point for the /runs/{run_id}/events API.
        For now, the behavior is:
        - Append the event to state.human_events
        - Re-run the workflow from the current state, treating the event
          as an additional signal
        - Update run status and result
        """
        run_data = self.run_store.get_run(run_id)
        if run_data is None:
            raise ValueError(f"Run {run_id} not found")

        state: RunState = run_data["state"]

        # Enrich event with metadata
        enriched_event: Dict[str, Any] = {
            **event,
            "received_at": datetime.now(timezone.utc).isoformat(),
        }

        human_events = list(state.get("human_events", []))
        human_events.append(enriched_event)

        # Prepare state for re-execution
        state = {
            **state,
            "human_events": human_events,
            "status": "running",
            "result": None,
        }

        logger.info(
            "human_event_received",
            run_id=run_id,
            trace_id=state.get("trace_id"),
            event_type=event.get("type"),
        )

        # Update stored state before re-execution
        self.run_store.update_run_state(run_id, state)

        # Re-execute workflow to incorporate human input
        final_state, result = self.executor.execute(run_id, state)
        self.run_store.update_run_state(run_id, final_state)
        self.run_store.update_run_status(
            run_id,
            final_state.get("status", "completed"),
            result,
        )

        return final_state

    def get_run(self, run_id: str) -> Dict[str, Any] | None:
        """Get run status and state.

        Args:
            run_id: Run identifier

        Returns:
            Run data dictionary or None if not found
        """
        return self.run_store.get_run(run_id)

