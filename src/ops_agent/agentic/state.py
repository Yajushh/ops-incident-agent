"""LangGraph state definition for the workflow."""

from typing import Annotated, Any

from typing_extensions import TypedDict

from ops_agent.agentic.schemas import IncidentActionPlan


class RunState(TypedDict):
    """State schema for the LangGraph workflow.

    This state flows through all nodes in the graph and is checkpointed
    at each step (in Chapter 3+).
    """

    # Input incident data
    incident: dict[str, Any]

    # Collected signals/metrics/logs
    signals: Annotated[list[dict[str, Any]], "append"]

    # Hypotheses generated during analysis
    hypotheses: Annotated[list[dict[str, Any]], "append"]

    # Results from tool invocations
    tool_results: Annotated[list[dict[str, Any]], "append"]

    # Actions to be taken
    actions: Annotated[list[dict[str, Any]], "append"]

    # Questions requiring human input
    open_questions: Annotated[list[str], "append"]

    # Human feedback/approvals/clarifications
    human_events: Annotated[list[dict[str, Any]], "append"]

    # Current workflow status
    status: str  # pending, running, completed, failed, paused

    # Final structured output (set when workflow completes)
    result: IncidentActionPlan | None

    # Trace ID for observability
    trace_id: str | None