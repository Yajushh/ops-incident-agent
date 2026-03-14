"""API integration tests using FastAPI TestClient."""

from fastapi.testclient import TestClient

from ops_agent.agentic.graph import create_workflow_graph
from ops_agent.agentic.tools.fake_metrics import FakeMetricsClient
from ops_agent.api.main import app
from ops_agent.application.executor import SyncWorkflowExecutor
from ops_agent.application.run_service import RunService
from ops_agent.infra.checkpoint_store import InMemoryCheckpointStore
from ops_agent.infra.run_store import InMemoryRunStore


def setup_test_app() -> TestClient:
    """Set up test app with explicit, fast in-memory dependencies."""
    metrics_client = FakeMetricsClient()
    graph = create_workflow_graph(metrics_client)
    checkpoint_store = InMemoryCheckpointStore()
    executor = SyncWorkflowExecutor(graph, checkpoint_store=checkpoint_store)
    run_store = InMemoryRunStore()
    app.state.run_service = RunService(executor, run_store)
    return TestClient(app)


def test_health_check():
    """Test health check endpoint."""
    client = setup_test_app()
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_create_run():
    """Test POST /runs endpoint."""
    client = setup_test_app()

    payload = {
        "title": "High latency on payment service",
        "description": "Payment processing is slow, customers complaining",
        "service": "payment-service",
        "environment": "production",
        "time_window": "2024-01-15T10:00:00Z/2024-01-15T11:00:00Z",
    }

    response = client.post("/runs", json=payload)

    assert response.status_code == 201
    data = response.json()
    assert "run_id" in data
    assert data["status"] == "completed"
    assert "trace_id" in data


def test_get_run():
    """Test GET /runs/{run_id} endpoint."""
    client = setup_test_app()

    # First create a run
    payload = {
        "title": "Service degradation",
        "description": "Multiple services reporting issues",
        "service": "api-service",
        "environment": "production",
        "time_window": "2024-01-15T10:00:00Z/2024-01-15T11:00:00Z",
    }

    create_response = client.post("/runs", json=payload)
    assert create_response.status_code == 201
    run_id = create_response.json()["run_id"]

    # Then retrieve it
    get_response = client.get(f"/runs/{run_id}")
    assert get_response.status_code == 200

    data = get_response.json()
    assert data["run"]["run_id"] == run_id
    assert data["run"]["status"] == "completed"
    assert data["state"] is not None
    assert data["result"] is not None

    # Verify result structure
    result = data["result"]
    assert "summary" in result
    assert "most_likely_cause" in result
    assert "confidence" in result
    assert "immediate_mitigations" in result


def test_get_nonexistent_run():
    """Test GET /runs/{run_id} with non-existent run."""
    client = setup_test_app()
    response = client.get("/runs/nonexistent-id")
    assert response.status_code == 404


def test_human_events_resume_run():
    """Test that POST /runs/{run_id}/events appends event and returns updated run."""
    client = setup_test_app()

    # Create a run first
    payload = {
        "title": "Test incident",
        "description": "Test",
        "service": "test-service",
        "environment": "production",
        "time_window": "2024-01-15T10:00:00Z/2024-01-15T11:00:00Z",
    }
    create_response = client.post("/runs", json=payload)
    run_id = create_response.json()["run_id"]

    # Try to submit human event
    response = client.post(
        f"/runs/{run_id}/events",
        json={"type": "approval", "actor": "oncall", "message": "Proceed with mitigation"},
    )
    assert response.status_code == 202
    data = response.json()
    assert data["run"]["run_id"] == run_id
    assert data["state"]["status"] == "completed"
    assert len(data["state"]["human_events"]) == 1

