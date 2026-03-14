"""In-memory checkpoint store implementation.

This implementation is intentionally simple but production-ready for
single-process deployments. It can be swapped out for a persistent
implementation (e.g. Postgres, Redis) without changing callers.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from ops_agent.agentic.state import RunState
from ops_agent.application.interfaces import CheckpointStore


@dataclass
class CheckpointRecord:
    """Represents a single checkpoint for a given run and step."""

    run_id: str
    step: str
    created_at: datetime
    state: RunState
    metadata: Dict[str, Any] = field(default_factory=dict)


class InMemoryCheckpointStore(CheckpointStore):
    """In-memory checkpoint store.

    Suitable for development, testing, and small single-instance
    deployments. For multi-instance production setups, replace with
    a shared store implementation behind the same interface.
    """

    def __init__(self) -> None:
        """Initialize empty store."""
        self._checkpoints: Dict[str, List[CheckpointRecord]] = {}

    def save_checkpoint(
        self, run_id: str, step: str, state: RunState, metadata: Optional[dict[str, Any]] = None
    ) -> None:
        """Save a checkpoint for a workflow step."""
        record = CheckpointRecord(
            run_id=run_id,
            step=step,
            created_at=datetime.now(timezone.utc),
            state=state,
            metadata=metadata or {},
        )
        self._checkpoints.setdefault(run_id, []).append(record)

    def get_checkpoint(self, run_id: str, step: str | None = None) -> dict[str, Any] | None:
        """Get the latest checkpoint or a specific step checkpoint."""
        records = self._checkpoints.get(run_id)
        if not records:
            return None

        if step is None:
            record = records[-1]
            return self._record_to_dict(record)

        # Find the last checkpoint for the given step
        for record in reversed(records):
            if record.step == step:
                return self._record_to_dict(record)

        return None

    def list_checkpoints(self, run_id: str) -> list[dict[str, Any]]:
        """List all checkpoints for a run."""
        records = self._checkpoints.get(run_id, [])
        return [self._record_to_dict(r) for r in records]

    @staticmethod
    def _record_to_dict(record: CheckpointRecord) -> dict[str, Any]:
        return {
            "run_id": record.run_id,
            "step": record.step,
            "created_at": record.created_at,
            "state": record.state,
            "metadata": record.metadata,
        }

