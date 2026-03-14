# Repository Tree

Complete file structure for the Ops Incident Response Agent repository.

```
ops-agent/
├── .gitignore                 # Git ignore rules
├── .python-version            # Python version (3.11)
├── ARCHITECTURE.md            # Architecture documentation
├── EXAMPLES.md                # API request/response examples
├── Makefile                   # Common development commands
├── README.md                  # Main documentation
├── REPOSITORY_TREE.md         # This file
├── pyproject.toml             # Dependencies and tool configs
│
├── src/ops_agent/             # Main package (src layout)
│   ├── __init__.py
│   │
│   ├── api/                   # FastAPI application layer
│   │   ├── __init__.py
│   │   ├── main.py            # FastAPI app, dependency injection
│   │   ├── models.py          # Request/response Pydantic models
│   │   └── routers/           # API route handlers
│   │       ├── __init__.py
│   │       └── runs.py        # /runs endpoints
│   │
│   ├── application/            # Application/business logic layer
│   │   ├── __init__.py
│   │   ├── executor.py        # SyncWorkflowExecutor (Chapter 1)
│   │   ├── interfaces.py      # Service interfaces (RunStore, CheckpointStore, etc.)
│   │   └── run_service.py     # Run lifecycle management
│   │
│   ├── agentic/               # LangGraph workflow layer
│   │   ├── __init__.py
│   │   ├── graph.py           # Workflow definition and compilation
│   │   ├── nodes.py           # Node implementations
│   │   ├── schemas.py         # Output schemas (IncidentActionPlan)
│   │   ├── state.py           # RunState TypedDict schema
│   │   └── tools/             # Tool interfaces and implementations
│   │       ├── __init__.py
│   │       ├── contracts.py   # Tool interfaces (MetricsClient, etc.)
│   │       └── fake_metrics.py # FakeMetricsClient (Chapter 1)
│   │
│   └── infra/                 # Infrastructure adapters
│       ├── __init__.py
│       ├── checkpoint_store.py # CheckpointStore interface (Chapter 3+)
│       ├── logging.py         # Structured JSON logging config
│       └── run_store.py       # InMemoryRunStore (Chapter 1)
│
└── tests/                     # Test suite
    ├── __init__.py
    ├── conftest.py            # Pytest fixtures
    ├── test_api.py            # API integration tests
    └── test_graph.py          # Workflow unit tests
```

## File Counts

- **Python files**: 24
- **Documentation files**: 4 (README, ARCHITECTURE, EXAMPLES, REPOSITORY_TREE)
- **Configuration files**: 3 (pyproject.toml, Makefile, .gitignore)
- **Total**: 31 files

## Key Directories

### `src/ops_agent/api/`
FastAPI application layer. Handles HTTP requests, validation, and responses.

### `src/ops_agent/application/`
Business logic and orchestration. Coordinates workflow execution and run management.

### `src/ops_agent/agentic/`
LangGraph workflow definitions, nodes, and state management. Core agentic logic.

### `src/ops_agent/infra/`
Infrastructure adapters: storage, logging, external integrations. Pluggable implementations.

### `tests/`
Test suite with unit tests for workflows and integration tests for API.

## Extension Points

All interfaces are defined in:
- `application/interfaces.py`: Service interfaces
- `agentic/tools/contracts.py`: Tool interfaces

New implementations can be added without changing existing code.

