import httpx
import logging
from typing import Set

logger = logging.getLogger(__name__)

TRENDING_API_URL = "https://api.coingecko.com/api/v3/search/trending"

async def get_trending_symbols() -> Set[str]:
    """
    Fetch trending search symbols from CoinGecko.
    Returns a set of uppercase symbols (e.g. {'BTC', 'SOL', 'SHIB'})
    """
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(TRENDING_API_URL)
            response.raise_for_status()
            data = response.json()
            
            trending_symbols = set()
            if "coins" in data:
                for item in data["coins"]:
                    coin = item.get("item", {})
                    symbol = coin.get("symbol")
                    if symbol:
                        trending_symbols.add(symbol.upper())
            
            logger.info(f"Fetched {len(trending_symbols)} trending symbols from CoinGecko")
            return trending_symbols
            
    except Exception as e:
        logger.error(f"Error fetching CoinGecko trending data: {e}")
        return set()
