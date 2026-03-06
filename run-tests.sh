#!/bin/bash
# Simple test runner for the prompt design workbench
# Usage: ./run-tests.sh [options]

set -e

echo "🧪 Running test suite..."
echo ""

uv run --with pytest python3 -m pytest tests/ -v --tb=short

echo ""
echo "✅ All tests completed!"
