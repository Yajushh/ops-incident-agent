"""Synchronous workflow executor.

Runs LangGraph workflows in the current thread. The concrete compiled
graph type varies across LangGraph versions, so we keep the type
annotation generic and only rely on its ``invoke`` method.
"""

from typing import Any

import structlog

from ops_agent.agentic.schemas import IncidentActionPlan
from ops_agent.agentic.state import RunState
from ops_agent.application.interfaces import CheckpointStore, WorkflowExecutor

logger = structlog.get_logger(__name__)


class SyncWorkflowExecutor(WorkflowExecutor):
    """Synchronous executor that runs workflows in the current thread.

    For Chapter 1, this executes the graph synchronously without checkpointing.
    Chapter 3 will add checkpointing support.
    """

    def __init__(
        self,
        graph: Any,
        checkpoint_store: CheckpointStore | None = None,
    ) -> None:
        """Initialize executor.

        Args:
            graph: Compiled LangGraph workflow
            checkpoint_store: Optional checkpoint store (not used in Chapter 1)
        """
        self.graph = graph
        self.checkpoint_store = checkpoint_store

    def execute(
        self, run_id: str, initial_state: RunState
    ) -> tuple[RunState, IncidentActionPlan | None]:
        """Execute workflow synchronously.

        Args:
            run_id: Run identifier
            initial_state: Starting state

        Returns:
            Tuple of (final_state, result)
        """
        logger.info("executing_workflow", run_id=run_id, trace_id=initial_state.get("trace_id"))

        try:
            # Optional: checkpoint initial state for replay and debugging
            if self.checkpoint_store is not None:
                self.checkpoint_store.save_checkpoint(
                    run_id=run_id,
                    step="initial",
                    state=initial_state,
                    metadata={"event": "before_execute"},
                )

            # Execute graph (synchronous for Chapter 1+)
            # LangGraph's invoke() runs the entire graph to completion
            final_state = self.graph.invoke(initial_state)

            result = final_state.get("result")
            status = final_state.get("status", "completed")

            # Persist final checkpoint if enabled
            if self.checkpoint_store is not None:
                self.checkpoint_store.save_checkpoint(
                    run_id=run_id,
                    step="final",
                    state=final_state,
                    metadata={"event": "after_execute", "status": status},
                )

            if status == "completed" and result:
                logger.info(
                    "workflow_completed",
                    run_id=run_id,
                    trace_id=final_state.get("trace_id"),
                )
                return final_state, result
            else:
                logger.warning(
                    "workflow_incomplete",
                    run_id=run_id,
                    status=status,
                    trace_id=final_state.get("trace_id"),
                )
                return final_state, None

        except Exception as e:
            logger.error(
                "workflow_execution_failed",
                run_id=run_id,
                error=str(e),
                trace_id=initial_state.get("trace_id"),
                exc_info=True,
            )
            # Update state with error
            error_state: RunState = {
                **initial_state,
                "status": "failed",
                "result": None,
            }
            if self.checkpoint_store is not None:
                self.checkpoint_store.save_checkpoint(
                    run_id=run_id,
                    step="error",
                    state=error_state,
                    metadata={"event": "exception", "error": str(e)},
                )
            return error_state, None

    def resume(self, run_id: str, human_input: dict) -> tuple[RunState, IncidentActionPlan | None]:
        """Resume a paused workflow.

        TODO: Implement in Chapter 5 when human-in-the-loop is added.

        Args:
            run_id: Run identifier
            human_input: Human feedback

        Returns:
            Tuple of (final_state, result)
        """
        raise NotImplementedError("Resume not implemented in Chapter 1")

