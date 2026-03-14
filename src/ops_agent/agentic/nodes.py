"""LangGraph node implementations.

Each node is a function that takes RunState and returns a partial state update.
"""

import structlog
from typing_extensions import TypedDict

from ops_agent.agentic.schemas import IncidentActionPlan
from ops_agent.agentic.state import RunState
from ops_agent.agentic.tools.contracts import MetricsClient

logger = structlog.get_logger(__name__)


def collect_metrics_node(
    state: RunState, metrics_client: MetricsClient
) -> TypedDict("PartialState", {"signals": list[dict], "tool_results": list[dict]}):
    """Node that collects metrics for the incident.

    This is a minimal node for Chapter 1 that:
    1. Queries latency and error rate metrics
    2. Stores results in state.signals and state.tool_results
    """
    incident = state["incident"]
    service = incident["service"]
    environment = incident["environment"]
    time_window = incident["time_window"]

    logger.info(
        "collecting_metrics",
        service=service,
        environment=environment,
        time_window=time_window,
        trace_id=state.get("trace_id"),
    )

    # Query metrics
    latency_data = metrics_client.query_latency(service, environment, time_window)
    error_data = metrics_client.query_error_rate(service, environment, time_window)

    # Store as signals
    signals = [
        {"type": "latency", "data": latency_data},
        {"type": "error_rate", "data": error_data},
    ]

    # Store tool results with IDs for reference
    tool_results = [
        {"tool": "metrics", "type": "latency", "result_id": "latency_001", "data": latency_data},
        {
            "tool": "metrics",
            "type": "error_rate",
            "result_id": "error_rate_001",
            "data": error_data,
        },
    ]

    return {
        "signals": signals,
        "tool_results": tool_results,
    }


def generate_action_plan_node(state: RunState) -> TypedDict(
    "PartialState", {"result": IncidentActionPlan, "status": str}
):
    """Node that generates the final IncidentActionPlan.

    For Chapter 1, this is a simple deterministic generator based on
    the collected metrics. In later chapters, this will use LLM reasoning.
    """
    incident = state["incident"]
    signals = state.get("signals", [])
    tool_results = state.get("tool_results", [])

    logger.info(
        "generating_action_plan",
        incident_title=incident.get("title"),
        signals_count=len(signals),
        trace_id=state.get("trace_id"),
    )

    # Extract key metrics from signals
    latency_signal = next((s for s in signals if s.get("type") == "latency"), None)
    error_signal = next((s for s in signals if s.get("type") == "error_rate"), None)

    # Simple heuristic for Chapter 1: if error rate > 3%, it's likely an error issue
    error_rate = 0.0
    if error_signal and "data" in error_signal:
        error_rate = error_signal["data"].get("error_rate", 0.0)

    # Generate action plan based on metrics
    if error_rate > 0.03:
        most_likely_cause = "High error rate detected - likely service degradation or dependency failure"
        confidence = 0.75
        immediate_mitigations = [
            "Enable circuit breakers for downstream dependencies",
            "Scale up service instances if resource-constrained",
            "Check for recent deployments that may have introduced bugs",
        ]
        supporting_evidence = [
            r["result_id"] for r in tool_results if r.get("type") == "error_rate"
        ]
    else:
        most_likely_cause = "Latency degradation - possible resource contention or slow dependencies"
        confidence = 0.65
        immediate_mitigations = [
            "Check database query performance",
            "Review downstream service latency",
            "Monitor resource utilization (CPU, memory, network)",
        ]
        supporting_evidence = [
            r["result_id"] for r in tool_results if r.get("type") == "latency"
        ]

    action_plan = IncidentActionPlan(
        summary=f"Incident analysis for {incident.get('title', 'unknown')}. "
        f"Detected {'high error rate' if error_rate > 0.03 else 'latency issues'} "
        f"in {incident.get('service')} ({incident.get('environment')}).",
        most_likely_cause=most_likely_cause,
        confidence=confidence,
        supporting_evidence=supporting_evidence,
        immediate_mitigations=immediate_mitigations,
        verification_steps=[
            "Monitor error rate and latency metrics for 15 minutes",
            "Verify that mitigations have reduced error rate below 1%",
            "Check service health endpoints",
        ],
        comms_template=f"Incident: {incident.get('title')}\n"
        f"Status: Investigating\n"
        f"Impact: {incident.get('service')} experiencing "
        f"{'errors' if error_rate > 0.03 else 'latency degradation'}\n"
        f"Mitigation: {immediate_mitigations[0] if immediate_mitigations else 'TBD'}",
        followups=[
            "Root cause analysis post-mortem",
            "Review monitoring and alerting thresholds",
            "Update runbooks with lessons learned",
        ],
        risk_notes="Medium risk - service degradation detected. "
        "If not mitigated quickly, may impact user experience.",
    )

    return {
        "result": action_plan,
        "status": "completed",
    }

