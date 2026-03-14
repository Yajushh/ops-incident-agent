# Architecture

This document describes the architecture of the Ops Incident Response Agent, focusing on how state flows through the system and how components interact.

## High-Level Architecture

```
┌─────────────┐
│   FastAPI   │  HTTP API Layer
│   Routers   │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ Run Service │  Application Layer (Orchestration)
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Executor   │  Workflow Execution
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ LangGraph   │  Agentic Workflow Engine
│  Workflow   │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│    Tools    │  External Integrations (Metrics, Logs, etc.)
└─────────────┘
```

## State Flow

### 1. Request → Initial State

When a `POST /runs` request arrives:

1. **API Layer** (`api/routers/runs.py`):
   - Validates `IncidentCreate` payload
   - Calls `RunService.create_and_execute_run()`

2. **Application Layer** (`application/run_service.py`):
   - Generates `run_id` and `trace_id`
   - Creates initial `RunState`:
     ```python
     {
       "incident": {...},      # From API request
       "signals": [],
       "hypotheses": [],
       "tool_results": [],
       "actions": [],
       "open_questions": [],
       "human_events": [],
       "status": "running",
       "result": None,
       "trace_id": "..."
     }
     ```
   - Stores run in `RunStore`
   - Calls `Executor.execute()`

### 2. Workflow Execution

The executor runs the LangGraph workflow:

1. **Graph Definition** (`agentic/graph.py`):
   - Defines nodes and edges
   - Compiles graph for execution

2. **Node Execution** (`agentic/nodes.py`):
   - Each node receives `RunState`
   - Node performs work (calls tools, processes data)
   - Node returns partial state update
   - LangGraph merges updates into state

3. **State Updates**:
   - `collect_metrics_node`: Adds to `signals` and `tool_results`
   - `generate_action_plan_node`: Sets `result` and `status="completed"`

### 3. Final State → Response

After execution:

1. **Executor** returns `(final_state, result)`
2. **Run Service** updates `RunStore` with final state
3. **API Layer** returns run_id to client

When client calls `GET /runs/{run_id}`:

1. **API Layer** calls `RunService.get_run()`
2. **Run Service** retrieves from `RunStore`
3. **API Layer** formats response with:
   - Run metadata (status, timestamps)
   - State snapshot
   - Final `IncidentActionPlan` (if completed)

## Component Details

### API Layer (`api/`)

**Responsibilities:**
- HTTP request/response handling
- Request validation (Pydantic models)
- Response serialization
- Error handling and status codes

**Key Files:**
- `api/main.py`: FastAPI app, dependency injection setup
- `api/routers/runs.py`: Run endpoints
- `api/models.py`: Request/response schemas

### Application Layer (`application/`)

**Responsibilities:**
- Run lifecycle management
- Workflow orchestration
- Business logic coordination

**Key Components:**
- `RunService`: Creates runs, executes workflows, manages state
- `SyncWorkflowExecutor`: Executes LangGraph workflows synchronously
- Interfaces: Define contracts for extensibility

### Agentic Layer (`agentic/`)

**Responsibilities:**
- Workflow definition (LangGraph)
- Node implementations
- State schema
- Tool interfaces

**Key Components:**
- `graph.py`: Workflow definition and compilation
- `nodes.py`: Individual workflow nodes
- `state.py`: TypedDict state schema
- `schemas.py`: Pydantic output schemas
- `tools/`: Tool interfaces and implementations

### Infrastructure Layer (`infra/`)

**Responsibilities:**
- Storage adapters
- Logging configuration
- External service clients

**Key Components:**
- `run_store.py`: In-memory run storage (Chapter 1)
- `checkpoint_store.py`: Checkpointing interface (Chapter 3+)
- `logging.py`: Structured JSON logging

## Checkpointing (Chapter 3+)

### Current State (Chapter 1)

- No checkpointing
- Synchronous execution
- State only stored at start and end

### Future State (Chapter 3+)

Checkpointing will enable:

1. **State Persistence**:
   - After each node execution
   - State stored in `CheckpointStore`
   - Enables pause/resume

2. **Pause/Resume Flow**:
   ```
   Workflow starts → Node 1 → Checkpoint → Node 2 → Checkpoint → ...
                                                      ↑
                                              (can pause here)
   ```

3. **Human-in-the-Loop** (Chapter 5):
   - Workflow pauses at human node
   - State checkpointed
   - Human provides input via `/runs/{run_id}/events`
   - Workflow resumes from checkpoint

4. **Deterministic Replay** (Chapter 6):
   - Load checkpoint
   - Replay from that point
   - Useful for testing and debugging

### Checkpoint Store Interface

```python
class CheckpointStore(ABC):
    def save_checkpoint(run_id, step, state, metadata)
    def get_checkpoint(run_id, step=None)  # Latest if step=None
    def list_checkpoints(run_id)
```

## Tool Architecture

### Interface-Based Design

All tools implement interfaces defined in `agentic/tools/contracts.py`:

- `MetricsClient`: Query metrics/telemetry
- `LogClient`: Search logs (Chapter 4+)
- `DeploymentClient`: Query deployments (Chapter 4+)

### Benefits

1. **Testability**: Easy to swap real tools with fakes
2. **Extensibility**: Add new tool types without changing workflow
3. **Pluggability**: Different implementations for different environments

### Chapter 1 Implementation

- `FakeMetricsClient`: Returns mock data
- Used in development and tests
- Real implementations added in Chapter 4+

## Logging and Observability

### Structured JSON Logging

All logs use `structlog` with JSON output:

```json
{
  "event": "executing_workflow",
  "run_id": "550e8400-...",
  "trace_id": "trace_550e8400",
  "timestamp": "2024-01-15T10:30:00Z",
  "level": "info"
}
```

### Correlation

- `run_id`: Correlates all logs for a single run
- `trace_id`: For distributed tracing (future)
- Context vars: Automatically added to all log entries

### Future Enhancements (Chapter 6+)

- OpenTelemetry integration
- Distributed tracing
- Metrics export
- Performance monitoring

## Extension Points

### Adding a New Tool

1. Define interface in `agentic/tools/contracts.py`
2. Implement in `agentic/tools/`
3. Inject into workflow graph
4. Use in nodes

### Adding a New Node

1. Implement node function in `agentic/nodes.py`
2. Add to graph in `agentic/graph.py`
3. Define edges/routing logic

### Adding Persistence

1. Implement `RunStore` interface (e.g., `PostgresRunStore`)
2. Implement `CheckpointStore` interface
3. Update dependency injection in `api/main.py`

### Adding Async Execution

1. Implement `AsyncWorkflowExecutor` (Chapter 7+)
2. Use background workers (Celery, RQ, etc.)
3. Update API to return immediately
4. Add polling endpoint for status

## Testing Strategy

### Unit Tests

- Test individual nodes with mock tools
- Test workflow graph execution
- Test state transformations

### Integration Tests

- Test API endpoints with TestClient
- Test full workflow execution
- Test error handling

### Future (Chapter 6)

- Golden tests with deterministic replay
- Regression test harness
- Performance benchmarks

## Dependencies

### Core

- **FastAPI**: Web framework
- **LangGraph**: Workflow engine
- **Pydantic**: Data validation and settings
- **structlog**: Structured logging

### Development

- **pytest**: Testing
- **mypy**: Type checking
- **ruff**: Linting and formatting

## Future Architecture Considerations

### Chapter 7+: Production Infrastructure

- **Database**: Postgres for persistent storage
- **Cache**: Redis for checkpointing and state caching
- **Queue**: Background job processing
- **Message Bus**: Kafka for event streaming (optional)
- **Containerization**: Docker for deployment
- **Orchestration**: Kubernetes (optional)

All of these will be added behind existing interfaces, maintaining clean separation of concerns.

