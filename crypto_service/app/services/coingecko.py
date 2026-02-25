import httpx
import logging
from typing import Set, Dict, Any, List

logger = logging.getLogger(__name__)

COINGECKO_BASE_URL = "https://api.coingecko.com/api/v3"
TRENDING_API_URL = f"{COINGECKO_BASE_URL}/search/trending"
MARKETS_API_URL = f"{COINGECKO_BASE_URL}/coins/markets"

COINGECKO_IDS_MAPPING = {
    'BTCUSDT': 'bitcoin',
    'ETHUSDT': 'ethereum',
    'SOLUSDT': 'solana',
    'BNBUSDT': 'binancecoin',
    'ARBUSDT': 'arbitrum',
    'OPUSDT': 'optimism',
    'POLUSDT': 'polygon-ecosystem-token',
    'AVAXUSDT': 'avalanche-2',
    'TRXUSDT': 'tron',
    'ADAUSDT': 'cardano',
    'DOTUSDT': 'polkadot',
    'NEARUSDT': 'near',
    'AAVEUSDT': 'aave',
    'UNIUSDT': 'uniswap',
    'LINKUSDT': 'chainlink',
    'ATOMUSDT': 'cosmos',
    'FILUSDT': 'filecoin',
    'LTCUSDT': 'litecoin',
    'XLMUSDT': 'stellar',
    'XRPUSDT': 'ripple',
    'DOGEUSDT': 'dogecoin',
    'ETCUSDT': 'ethereum-classic',
}

async def get_trending_symbols() -> Set[str]:
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(TRENDING_API_URL)
            response.raise_for_status()
            data = response.json()
            
            trending_identifiers = set()
            if "coins" in data:
                for item in data["coins"]:
                    coin = item.get("item", {})
                    symbol = coin.get("symbol")
                    coin_id = coin.get("id")
                    if symbol:
                        trending_identifiers.add(symbol.upper())
                    if coin_id:
                        trending_identifiers.add(coin_id.lower())
            
            logger.info(f"Fetched {len(trending_identifiers)} trending identifiers from CoinGecko")
            return trending_identifiers
            
    except Exception as e:
        logger.error(f"Error fetching CoinGecko trending data: {e}")
        return set()

async def get_coins_markets_data(symbols: List[str]) -> Dict[str, Dict[str, Any]]:
    try:
        cg_ids = [COINGECKO_IDS_MAPPING.get(s) for s in symbols if s in COINGECKO_IDS_MAPPING]
        if not cg_ids:
            return {}

        ids_str = ",".join(cg_ids)
        params = {
            "vs_currency": "usd",
            "ids": ids_str,
            "order": "market_cap_desc",
            "per_page": 250,
            "page": 1,
            "sparkline": "false"
        }

        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(MARKETS_API_URL, params=params)
            response.raise_for_status()
            data = response.json()

        results = {}
        cg_data_map = {coin["id"]: coin for coin in data}

        for symbol in symbols:
            cg_id = COINGECKO_IDS_MAPPING.get(symbol)
            if cg_id and cg_id in cg_data_map:
                coin_data = cg_data_map[cg_id]
                results[symbol] = {
                    "tvl": coin_data.get("market_cap"),
                    "change_1d": coin_data.get("price_change_percentage_24h"),
                    "cg_id": cg_id,
                    "rank": coin_data.get("market_cap_rank")
                }
        
        logger.info(f"Fetched CoinGecko market data for {len(results)} coins")
        return results

    except Exception as e:
        logger.error(f"Error fetching CoinGecko market data: {e}")
        return {}
