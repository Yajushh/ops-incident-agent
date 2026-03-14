"""Pytest configuration and fixtures."""

import pytest

from ops_agent.agentic.graph import create_workflow_graph
from ops_agent.agentic.tools.fake_metrics import FakeMetricsClient
from ops_agent.application.executor import SyncWorkflowExecutor
from ops_agent.application.run_service import RunService
from ops_agent.infra.run_store import InMemoryRunStore


@pytest.fixture
def metrics_client() -> FakeMetricsClient:
    """Fixture for fake metrics client."""
    return FakeMetricsClient()


@pytest.fixture
def workflow_graph(metrics_client: FakeMetricsClient):
    """Fixture for compiled workflow graph."""
    return create_workflow_graph(metrics_client)


@pytest.fixture
def executor(workflow_graph):
    """Fixture for workflow executor."""
    return SyncWorkflowExecutor(workflow_graph)


@pytest.fixture
def run_store() -> InMemoryRunStore:
    """Fixture for in-memory run store."""
    return InMemoryRunStore()


@pytest.fixture
def run_service(executor: SyncWorkflowExecutor, run_store: InMemoryRunStore) -> RunService:
    """Fixture for run service."""
    return RunService(executor, run_store)

