import pytest
from unittest.mock import patch
from app.services.defillama.chains import get_chain_1d_change, get_chains_tvl
from app.services.defillama.global_stats import get_global_stats

class DummyResponse:
    def __init__(self, json_data):
        self._json = json_data
        self.status_code = 200
    def json(self):
        return self._json
    def raise_for_status(self):
        pass

@pytest.mark.asyncio
async def test_get_chain_1d_change_success():
    mock_data = [{"tvl": 100}, {"tvl": 150}, {"tvl": 150}, {"tvl": 120}]
    
    class StubClient:
        def __init__(self, *args, **kwargs): pass
        async def __aenter__(self): return self
        async def __aexit__(self, *args): pass
        async def get(self, url, *args, **kwargs):
            return DummyResponse(mock_data)
            
    with patch("app.services.defillama.chains.httpx.AsyncClient", new=StubClient):
        change = await get_chain_1d_change("solana")
        assert change == -20.0

@pytest.mark.asyncio
async def test_get_chain_1d_change_is_protocol():
    change = await get_chain_1d_change("lido", is_protocol=True)
    assert change == 0.0

@pytest.mark.asyncio
async def test_get_chains_tvl_success():
    mock_data = [
        {"name": "Bitcoin", "tvl": 1000, "change_1d": 5.0, "mcap": 20000},
        {"name": "Ethereum", "tvl": 5000, "change_1d": 2.0, "mcap": 10000}
    ]
    
    class StubClient:
        def __init__(self, *args, **kwargs): pass
        async def __aenter__(self): return self
        async def __aexit__(self, *args): pass
        async def get(self, url, *args, **kwargs):
            return DummyResponse(mock_data)
            
    with patch("app.services.defillama.chains.httpx.AsyncClient", new=StubClient):
        tvl = await get_chains_tvl()
        assert "Bitcoin" in tvl
        assert tvl["Bitcoin"]["tvl"] == 1000
        assert tvl["Ethereum"]["change_1d"] == 2.0

@pytest.mark.asyncio
async def test_get_global_stats():
    tvl_data = {
        "Bitcoin": {"tvl": 1000},
        "Ethereum": {"tvl": 2000},
        "Solana": {"tvl": 500}
    }
    
    stats = await get_global_stats(tvl_data=tvl_data)
    
    assert stats["total_tvl"] == 3500
    assert stats["chain_count"] == 3
