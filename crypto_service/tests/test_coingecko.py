import pytest
from unittest.mock import patch
from app.services.coingecko import get_trending_symbols

class DummyResponse:
    def __init__(self, json_data):
        self._json = json_data
        self.status_code = 200
    def json(self):
        return self._json
    def raise_for_status(self):
        pass

@pytest.mark.asyncio
async def test_get_trending_symbols_success():
    mock_data = {
        "coins": [
            {"item": {"symbol": "btc"}},
            {"item": {"symbol": "SOL"}},
            {"item": {"symbol": "doge"}}
        ]
    }
    
    class StubClient:
        def __init__(self, *args, **kwargs): pass
        async def __aenter__(self): return self
        async def __aexit__(self, *args): pass
        async def get(self, url, *args, **kwargs):
            return DummyResponse(mock_data)

    with patch("app.services.coingecko.httpx.AsyncClient", new=StubClient):
        symbols = await get_trending_symbols()
        
        assert len(symbols) == 3
        assert "BTC" in symbols
        assert "SOL" in symbols
        assert "DOGE" in symbols

@pytest.mark.asyncio
async def test_get_trending_symbols_error():
    class StubClientError:
        def __init__(self, *args, **kwargs): pass
        async def __aenter__(self): return self
        async def __aexit__(self, *args): pass
        async def get(self, url, *args, **kwargs):
            raise Exception("API fetch failed")

    with patch("app.services.coingecko.httpx.AsyncClient", new=StubClientError):
        symbols = await get_trending_symbols()
        assert symbols == set()
