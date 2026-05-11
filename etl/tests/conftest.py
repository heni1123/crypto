import pytest
from unittest import mock

@pytest.fixture
def sample_records():
    """Provides a list of valid records matching the crypto_market_snapshot schema."""
    return [
        {"id": "1", "name": "Bitcoin", "symbol": "BTC", "current_price": 50000.0, "market_cap": 900000000000},
        {"id": "2", "name": "Ethereum", "symbol": "ETH", "current_price": 4000.0, "market_cap": 400000000000},
        {"id": "3", "name": "Ripple", "symbol": "XRP", "current_price": 1.0, "market_cap": 50000000000},
    ]

@pytest.fixture
def empty_records():
    """Provides an empty list of records."""
    return []

@pytest.fixture
def invalid_records():
    """Provides a list of records with missing/null required fields."""
    return [
        {"id": "1", "name": None, "symbol": "BTC", "current_price": 50000.0, "market_cap": 900000000000},
        {"id": "2", "name": "Ethereum", "symbol": "ETH", "current_price": None, "market_cap": 400000000000},
        {},
    ]

@pytest.fixture
async def mock_db_connection():
    """Mocks asyncpg.Connection or sqlalchemy Engine connection."""
    with mock.patch('asyncpg.connect', create=True) as mock_connect:
        mock_conn = mock.AsyncMock()
        mock_conn.fetch.return_value = [{"id": "1", "name": "Bitcoin"}]
        mock_conn.execute.return_value = None
        mock_conn.fetchrow.return_value = {"id": "1", "name": "Bitcoin"}
        mock_conn.fetchval.return_value = "1"
        mock_connect.return_value = mock_conn
        yield mock_conn

@pytest.fixture
async def mock_http_session():
    """Mocks aiohttp.ClientSession."""
    with mock.patch('aiohttp.ClientSession', create=True) as mock_session:
        mock_instance = mock.AsyncMock()
        mock_instance.get.return_value.__aenter__.return_value = mock.AsyncMock(json=mock.AsyncMock(return_value={"data": "value"}))
        mock_instance.post.return_value.__aenter__.return_value = mock.AsyncMock(json=mock.AsyncMock(return_value={"data": "value"}))
        mock_session.return_value = mock_instance
        yield mock_instance

pytest_plugins = ["pytest_asyncio"]
asyncio_mode = "auto"