#!/usr/bin/env bash
set -e
echo "=== Installing test dependencies ==="
pip install pytest pytest-asyncio pytest-cov --quiet
echo "=== Running unit tests ==="
python -m pytest tests/ -v --tb=short
echo "=== Running full suite with coverage ==="
python -m pytest tests/ --cov=. --cov-report=term-missing --cov-report=html:coverage_html -v
echo "=== Done ==="
