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
	@echo "Passing Arguments:"
	@echo "  make test ARGS=\"-k test_default\"         Run specific tests"
	@echo "  make test-coverage ARGS=\"-v --tb=long\"   Tests with custom args"
	@echo "  make design SPEC=my-spec.md ARGS=\"--model gpt-4o\""
	@echo "  make lint ARGS=\"--fix\"                   Fix linting issues"
	@echo "  make format ARGS=\"--line-length 100\""
	@echo ""

install:
	uv sync

test:
	uv run --with pytest python3 -m pytest tests/ -v $(ARGS)

test-coverage:
	uv run --with pytest --with pytest-cov python3 -m pytest tests/ --cov=prompt_design_system --cov-report=term $(ARGS)

design:
	uv run promptctl design $(SPEC) $(ARGS)

run:
	uv run promptctl $(ARGS)

lint:
	uv run ruff check prompt_design_system/ $(ARGS)

format:
	uv run ruff format prompt_design_system/ $(ARGS)

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".coverage" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
