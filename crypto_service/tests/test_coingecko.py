import pytest
from unittest.mock import patch
from app.services.coingecko import get_trending_symbols, get_coins_markets_data

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
    
    with patch("app.services.coingecko.httpx.AsyncClient.get") as mock_get:
        mock_get.return_value = DummyResponse(mock_data)
        symbols = await get_trending_symbols()
        
        assert len(symbols) == 3
        assert "BTC" in symbols
        assert "SOL" in symbols
        assert "DOGE" in symbols

@pytest.mark.asyncio
async def test_get_coins_markets_data():
    mock_data = [
        {"id": "bitcoin", "total_value_locked": 1000, "price_change_percentage_24h": 5.0},
        {"id": "ethereum", "total_value_locked": 500, "price_change_percentage_24h": -2.0}
    ]
    
    with patch("app.services.coingecko.httpx.AsyncClient.get") as mock_get:
        mock_get.return_value = DummyResponse(mock_data)
        results = await get_coins_markets_data(["BTCUSDT", "ETHUSDT"])
        
        assert "BTCUSDT" in results
        assert results["BTCUSDT"]["tvl"] == 1000
        assert results["BTCUSDT"]["change_1d"] == 5.0
        assert "ETHUSDT" in results
        assert results["ETHUSDT"]["tvl"] == 500
