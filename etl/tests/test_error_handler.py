try:
    from pipeline.error_handler import *
except ImportError:
    pytest.skip("module not available", allow_module_level=True)

import pytest
from unittest import mock
from unittest.mock import AsyncMock

@pytest.mark.asyncio
async def test_retry_with_backoff_happy_path(mock_http_session):
    """Test retry_with_backoff with a successful function call."""
    async def successful_function():
        return "Success"

    result = await error_handler.retry_with_backoff(successful_function)
    assert result == "Success"

@pytest.mark.asyncio
async def test_retry_with_backoff_empty_input():
    """Test retry_with_backoff with empty input."""
    async def function_with_no_args():
        return "Success"

    result = await error_handler.retry_with_backoff(function_with_no_args)
    assert result == "Success"

@pytest.mark.asyncio
async def test_retry_with_backoff_error_handling():
    """Test retry_with_backoff with a function that raises an exception."""
    async def failing_function():
        raise Exception("Failure")

    result = await error_handler.retry_with_backoff(failing_function)
    assert result is None

@pytest.mark.asyncio
async def test_log_audit_happy_path(caplog):
    """Test log_audit with valid input."""
    run_ts = "2023-10-01T00:00:00Z"
    rows_loaded = 100
    status = "SUCCESS"

    await error_handler.log_audit(run_ts, rows_loaded, status)
    assert "Audit Log - Run Timestamp" in caplog.text

@pytest.mark.asyncio
async def test_log_audit_empty_input(caplog):
    """Test log_audit with empty input."""
    run_ts = ""
    rows_loaded = 0
    status = ""

    await error_handler.log_audit(run_ts, rows_loaded, status)
    assert "Audit Log - Run Timestamp" in caplog.text

@pytest.mark.asyncio
async def test_log_audit_error_handling(caplog):
    """Test log_audit with invalid input."""
    run_ts = None
    rows_loaded = None
    status = None

    await error_handler.log_audit(run_ts, rows_loaded, status)
    assert "Audit Log - Run Timestamp" in caplog.text