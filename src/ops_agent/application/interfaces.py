"""Interfaces for application layer components.

These interfaces enable dependency injection and make the system
testable and extensible.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any

from ops_agent.agentic.state import RunState
from ops_agent.agentic.schemas import IncidentActionPlan


class RunStore(ABC):
    """Interface for storing and retrieving run metadata and state.

    Implementations:
    - InMemoryRunStore: Dict-based storage (Chapter 1-3)
    - PostgresRunStore: Persistent storage (Chapter 7+)
    """

    @abstractmethod
    def create_run(
        self, run_id: str, trace_id: str | None, initial_state: RunState
    ) -> None:
        """Create a new run record.

        Args:
            run_id: Unique identifier for the run
            trace_id: Optional trace ID for observability
            initial_state: Initial workflow state
        """
        pass

    @abstractmethod
    def get_run(self, run_id: str) -> dict[str, Any] | None:
        """Get run metadata and current state.

        Args:
            run_id: Run identifier

        Returns:
            Dictionary with run metadata and state, or None if not found
        """
        pass

    @abstractmethod
    def update_run_state(self, run_id: str, state: RunState) -> None:
        """Update the state for a run.

        Args:
            run_id: Run identifier
            state: Updated state
        """
        pass

    @abstractmethod
    def update_run_status(
        self, run_id: str, status: str, result: IncidentActionPlan | None = None
    ) -> None:
        """Update run status and optionally final result.

        Args:
            run_id: Run identifier
            status: New status (running, completed, failed, paused)
            result: Final action plan if completed
        """
        pass


class CheckpointStore(ABC):
    """Interface for checkpointing workflow state.

    Checkpoints enable:
    - Pause/resume workflows
    - State inspection at any point
    - Deterministic replay for tests

    Implementations:
    - InMemoryCheckpointStore: Dict-based (Chapter 3)
    - RedisCheckpointStore: Redis-backed (Chapter 7+)
    - PostgresCheckpointStore: Persistent (Chapter 7+)
    """

    @abstractmethod
    def save_checkpoint(
        self, run_id: str, step: str, state: RunState, metadata: dict[str, Any] | None = None
    ) -> None:
        """Save a checkpoint for a workflow step.

        Args:
            run_id: Run identifier
            step: Step/node name
            state: State snapshot
            metadata: Optional metadata (timestamp, node config, etc.)
        """
        pass

    @abstractmethod
    def get_checkpoint(self, run_id: str, step: str | None = None) -> dict[str, Any] | None:
        """Get the latest checkpoint or a specific step checkpoint.

        Args:
            run_id: Run identifier
            step: Optional step name (if None, returns latest)

        Returns:
            Checkpoint data with state and metadata, or None if not found
        """
        pass

    @abstractmethod
    def list_checkpoints(self, run_id: str) -> list[dict[str, Any]]:
        """List all checkpoints for a run.

        Args:
            run_id: Run identifier

        Returns:
            List of checkpoint records
        """
        pass


class WorkflowExecutor(ABC):
    """Interface for executing workflows.

    Implementations:
    - SyncWorkflowExecutor: Synchronous execution (Chapter 1-2)
    - AsyncWorkflowExecutor: Async execution with background workers (Chapter 7+)
    """

    @abstractmethod
    def execute(
        self, run_id: str, initial_state: RunState
    ) -> tuple[RunState, IncidentActionPlan | None]:
        """Execute a workflow from initial state.

        Args:
            run_id: Run identifier
            initial_state: Starting state

        Returns:
            Tuple of (final_state, result) where result is None if workflow failed/paused
        """
        pass

    @abstractmethod
    def resume(self, run_id: str, human_input: dict[str, Any]) -> tuple[RunState, IncidentActionPlan | None]:
        """Resume a paused workflow with human input.

        Args:
            run_id: Run identifier
            human_input: Human feedback/approval/clarification

        Returns:
            Tuple of (final_state, result)
        """
        pass


class ObservabilityAdapter(ABC):
    """Interface for observability (tracing, metrics, logging).

    TODO: Implement in Chapter 6+
    """

    @abstractmethod
    def start_trace(self, run_id: str, operation: str) -> str:
        """Start a new trace span.

        Args:
            run_id: Run identifier
            operation: Operation name

        Returns:
            Trace ID
        """
        pass

    @abstractmethod
    def log_state_transition(
        self, run_id: str, trace_id: str, from_node: str, to_node: str, state: RunState
    ) -> None:
        """Log a state transition in the workflow.

        Args:
            run_id: Run identifier
            trace_id: Trace ID
            from_node: Source node
            to_node: Target node
            state: Current state
        """
        pass

