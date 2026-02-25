import httpx
import logging
from typing import Dict, Any

from app.services.defillama.config import DEFILLAMA_STABLES_URL

logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36",
    "Accept": "application/json",
}

async def get_stablecoin_flows() -> Dict[str, Dict[str, Any]]:
    try:
        async with httpx.AsyncClient(timeout=15.0, headers=HEADERS) as client:
            response = await client.get(DEFILLAMA_STABLES_URL)
            response.raise_for_status()
            data = response.json()

        flow_map = {}
        for chain in data:
            name = chain.get("name")
            if name:
                current = chain.get("totalCirculating", {}).get("peggedUSD", 0)
                prev = chain.get("circulatingPrevDay", {}).get("peggedUSD", 0)
                flow_map[name] = {
                    "mcap": current,
                    "net_change_1d": prev,
                    "net_flow_1d": current - prev
                }

        return flow_map

    except Exception as e:
        logger.error(f"Error fetching stablecoin flows: {e}")
        return {}
