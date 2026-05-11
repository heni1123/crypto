try:
    from extractors.coingecko_markets_api_api_extractor import *
except ImportError:
    pytest.skip("module not available", allow_module_level=True)

import pytest
from unittest import mock
from unittest.mock import AsyncMock

@pytest.mark.asyncio
async def test_extract_happy_path(mock_http_session):
    """Test extract method with valid input, expect success."""
    mock_http_session.get.return_value = AsyncMock(status=200, json=AsyncMock(return_value=[{"id": "bitcoin", "symbol": "btc"}]))
    extractor = CoingeckoMarketsApiExtractor({"url": "http://mockurl.com", "params": {}})
    result = await extractor.extract()
    assert result == [{"id": "bitcoin", "symbol": "btc"}]

@pytest.mark.asyncio
async def test_extract_empty_input():
    """Test extract method with empty input, expect empty list."""
    extractor = CoingeckoMarketsApiExtractor({"url": "http://mockurl.com", "params": {}})
    result = await extractor.extract()
    assert result == []

@pytest.mark.asyncio
async def test_extract_error_handling(mock_http_session):
    """Test extract method error handling with an exception."""
    mock_http_session.get.side_effect = Exception("Network error")
    extractor = CoingeckoMarketsApiExtractor({"url": "http://mockurl.com", "params": {}})
    result = await extractor.extract()
    assert result == []

@pytest.mark.asyncio
async def test_fetch_page_happy_path(mock_http_session):
    """Test _fetch_page method with valid parameters, expect success."""
    mock_http_session.get.return_value = AsyncMock(status=200, json=AsyncMock(return_value=[{"id": "ethereum", "symbol": "eth"}]))
    extractor = CoingeckoMarketsApiExtractor({"url": "http://mockurl.com", "params": {}})
    result = await extractor._fetch_page({"param": "value"})
    assert result == [{"id": "ethereum", "symbol": "eth"}]

@pytest.mark.asyncio
async def test_fetch_page_empty_input():
    """Test _fetch_page method with empty parameters, expect error handling."""
    extractor = CoingeckoMarketsApiExtractor({"url": "http://mockurl.com", "params": {}})
    result = await extractor._fetch_page({})
    assert result is None

@pytest.mark.asyncio
async def test_fetch_page_error_handling(mock_http_session):
    """Test _fetch_page method error handling with a non-200 response."""
    mock_http_session.get.return_value = AsyncMock(status=500)
    extractor = CoingeckoMarketsApiExtractor({"url": "http://mockurl.com", "params": {}})
    result = await extractor._fetch_page({"param": "value"})
    assert result is None

@pytest.mark.asyncio
async def test_handle_rate_limit(mock_http_session):
    """Test _handle_rate_limit method with a 429 response, expect wait."""
    mock_http_session.get.return_value = AsyncMock(status=429)
    extractor = CoingeckoMarketsApiExtractor({"url": "http://mockurl.com", "params": {}})
    await extractor._handle_rate_limit(mock_http_session.get.return_value)
    # Check if the method waits for the specified time (mocking time.sleep is needed)

@pytest.mark.asyncio
async def test_retry_with_backoff_happy_path(mock_http_session):
    """Test _retry_with_backoff method with successful retry."""
    mock_http_session.get.side_effect = [Exception("Network error"), AsyncMock(status=200, json=AsyncMock(return_value=[{"id": "litecoin", "symbol": "ltc"}]))]
    extractor = CoingeckoMarketsApiExtractor({"url": "http://mockurl.com", "params": {}})
    result = await extractor._retry_with_backoff(mock_http_session.get, "http://mockurl.com")
    assert result == [{"id": "litecoin", "symbol": "ltc"}]

@pytest.mark.asyncio
async def test_retry_with_backoff_max_retries_exceeded(mock_http_session):
    """Test _retry_with_backoff method when max retries are exceeded."""
    mock_http_session.get.side_effect = Exception("Network error")
    extractor = CoingeckoMarketsApiExtractor({"url": "http://mockurl.com", "params": {}})
    with pytest.raises(Exception, match="Max retries exceeded"):
        await extractor._retry_with_backoff(mock_http_session.get, "http://mockurl.com")

@pytest.mark.asyncio
async def test_close():
    """Test close method to ensure session is closed."""
    extractor = CoingeckoMarketsApiExtractor({"url": "http://mockurl.com", "params": {}})
    await extractor.close()
    assert extractor.session.closed is True