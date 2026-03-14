"""Unit tests for LangGraph workflow."""

from ops_agent.agentic.graph import create_workflow_graph
from ops_agent.agentic.state import RunState
from ops_agent.agentic.tools.fake_metrics import FakeMetricsClient


def test_workflow_execution(workflow_graph, metrics_client: FakeMetricsClient):
    """Test that the workflow executes end-to-end and produces an action plan."""
    # Create initial state
    initial_state: RunState = {
        "incident": {
            "title": "High latency on API service",
            "description": "Users reporting slow response times",
            "service": "api-service",
            "environment": "production",
            "time_window": "2024-01-15T10:00:00Z/2024-01-15T11:00:00Z",
        },
        "signals": [],
        "hypotheses": [],
        "tool_results": [],
        "actions": [],
        "open_questions": [],
        "human_events": [],
        "status": "running",
        "result": None,
        "trace_id": "test_trace_001",
    }

    # Execute workflow
    final_state = workflow_graph.invoke(initial_state)

    # Assertions
    assert final_state["status"] == "completed"
    assert final_state["result"] is not None

    # Check that metrics were collected
    assert len(final_state["signals"]) > 0
    assert len(final_state["tool_results"]) > 0

    # Check action plan structure
    action_plan = final_state["result"]
    assert action_plan.summary is not None
    assert action_plan.most_likely_cause is not None
    assert 0.0 <= action_plan.confidence <= 1.0
    assert len(action_plan.immediate_mitigations) > 0
    assert len(action_plan.verification_steps) > 0


def test_workflow_with_high_error_rate(workflow_graph):
    """Test workflow behavior when error rate is high."""
    # Mock metrics client that returns high error rate
    class HighErrorMetricsClient(FakeMetricsClient):
        def query_error_rate(self, service: str, environment: str, time_window: str):
            data = super().query_error_rate(service, environment, time_window)
            data["error_rate"] = 0.10  # 10% error rate
            return data

    high_error_client = HighErrorMetricsClient()
    graph = create_workflow_graph(high_error_client)

    initial_state: RunState = {
        "incident": {
            "title": "Service errors",
            "description": "High error rate detected",
            "service": "api-service",
            "environment": "production",
            "time_window": "2024-01-15T10:00:00Z/2024-01-15T11:00:00Z",
        },
        "signals": [],
        "hypotheses": [],
        "tool_results": [],
        "actions": [],
        "open_questions": [],
        "human_events": [],
        "status": "running",
        "result": None,
        "trace_id": "test_trace_002",
    }

    final_state = graph.invoke(initial_state)

    assert final_state["status"] == "completed"
    assert final_state["result"] is not None
    # Should identify error rate as the issue
    assert "error" in final_state["result"].most_likely_cause.lower()

