import pytest
from unittest.mock import patch
from app.services.fear_greed import get_fear_greed_index

class DummyResponse:
    def __init__(self, json_data):
        self._json = json_data
        self.status_code = 200
    def json(self):
        return self._json
    def raise_for_status(self):
        pass

@pytest.mark.asyncio
async def test_get_fear_greed_index_success():
    mock_data = {
        "name": "Fear and Greed Index", 
        "data": [
            {"value": "25", "value_classification": "Extreme Fear", "timestamp": "1234567890"}
        ],
        "metadata": {
            "time_until_update": "100"
        }
    }
    
    class StubClient:
        def __init__(self, *args, **kwargs): pass
        async def __aenter__(self): return self
        async def __aexit__(self, *args): pass
        async def get(self, url, *args, **kwargs):
            return DummyResponse(mock_data)
            
    with patch("app.services.fear_greed.httpx.AsyncClient", new=StubClient):
        result = await get_fear_greed_index()
        
        assert result is not None
        assert result["value"] == 25
        assert result["value_classification"] == "Extreme Fear"
        assert result["timestamp"] == "1234567890"

@pytest.mark.asyncio
async def test_get_fear_greed_index_empty():
    mock_data = {"data": []}
    
    class StubClient:
        def __init__(self, *args, **kwargs): pass
        async def __aenter__(self): return self
        async def __aexit__(self, *args): pass
        async def get(self, url, *args, **kwargs):
            return DummyResponse(mock_data)
            
    with patch("app.services.fear_greed.httpx.AsyncClient", new=StubClient):
        result = await get_fear_greed_index()
        assert result is None

@pytest.mark.asyncio
async def test_get_fear_greed_index_error():
    class StubClientError:
        def __init__(self, *args, **kwargs): pass
        async def __aenter__(self): return self
        async def __aexit__(self, *args): pass
        async def get(self, url, *args, **kwargs):
            raise Exception("Connection Failed")

    with patch("app.services.fear_greed.httpx.AsyncClient", new=StubClientError):
        result = await get_fear_greed_index()
        assert result is None
