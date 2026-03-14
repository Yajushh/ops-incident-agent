.PHONY: run lint typecheck test

run:
	uvicorn ops_agent.api.main:app --reload

lint:
	ruff check .
	ruff format --check .

typecheck:
	mypy src

test:
	pytest
