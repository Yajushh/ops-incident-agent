"""FastAPI application entry point."""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from ops_agent.agentic.graph import create_workflow_graph
from ops_agent.agentic.tools.fake_metrics import FakeMetricsClient
from ops_agent.api.routers import runs
from ops_agent.application.executor import SyncWorkflowExecutor
from ops_agent.application.run_service import RunService
from ops_agent.infra.logging import configure_logging
from ops_agent.infra.run_store import InMemoryRunStore
from ops_agent.infra.checkpoint_store import InMemoryCheckpointStore


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: setup and teardown."""
    # Configure logging
    configure_logging()

    # Initialize dependencies
    # Chapter 1: Use fake metrics client
    metrics_client = FakeMetricsClient()

    # Create workflow graph
    graph = create_workflow_graph(metrics_client)

    # Create checkpoint store (in-memory for Chapter 3)
    checkpoint_store = InMemoryCheckpointStore()

    # Create executor
    executor = SyncWorkflowExecutor(graph, checkpoint_store=checkpoint_store)

    # Create run store
    run_store = InMemoryRunStore()

    # Create service
    service = RunService(executor, run_store)

    # Store in app state for dependency injection
    app.state.run_service = service

    yield

    # Cleanup (if needed in future chapters)
    pass


# Create FastAPI app
app = FastAPI(
    title="Ops Incident Response Agent",
    description="LangGraph-powered incident triage and response planning service",
    version="0.1.0",
    lifespan=lifespan,
)


# Dependency injection for routers
def get_run_service() -> RunService:
    """Get run service from app state."""
    return app.state.run_service


# Include routers
app.include_router(runs.router)


@app.get("/health")
def health_check() -> dict:
    """Health check endpoint."""
    return {"status": "healthy", "version": "0.1.0"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)

