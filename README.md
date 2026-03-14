# Ops Agent (Chapter 1)

This chapter implements a minimal end-to-end Ops Incident Response Agent:

- FastAPI endpoints:
  - POST /runs: execute the LangGraph workflow synchronously and return a structured result
  - GET /runs/{run_id}: fetch stored run snapshot
- LangGraph workflow (minimal):
  1. Intake + Normalize
  2. Call one tool (Fake Metrics)
  3. Synthesize IncidentActionPlan (Pydantic)

## Run

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
make run
```
