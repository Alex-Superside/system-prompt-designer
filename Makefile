.PHONY: help test test-coverage design run lint format install clean

help:
	@echo "Prompt Design Workbench - Available Commands"
	@echo ""
	@echo "Setup:"
	@echo "  make install          Install dependencies with uv"
	@echo ""
	@echo "Testing:"
	@echo "  make test             Run all 324 tests"
	@echo "  make test-coverage    Run tests with coverage report"
	@echo ""
	@echo "Code Quality:"
	@echo "  make lint             Check code with ruff"
	@echo "  make format           Format code with ruff"
	@echo ""
	@echo "Running:"
	@echo "  make design           Run design on sample spec"
	@echo "  make run              Start interactive CLI"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean            Remove cache/build files"
	@echo ""

install:
	uv pip install -e .

test:
	uv run --with pytest python3 -m pytest tests/ -v

test-coverage:
	uv run --with pytest --with pytest-cov python3 -m pytest tests/ --cov=prompt_design_system --cov-report=term

design:
	uv run promptctl design test-agent.agent-spec.md

run:
	uv run promptctl --help

lint:
	uv run ruff check prompt_design_system/

format:
	uv run ruff format prompt_design_system/

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".coverage" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
