import httpx
import logging
import asyncio
from typing import Dict, Any

from app.services.defillama.config import DEFILLAMA_CHANS_URL, HISTORY_SLUG_OVERRIDES

logger = logging.getLogger(__name__)

async def get_chain_1d_change(slug: str, is_protocol: bool = False) -> float:
    try:
        if is_protocol:
            return 0.0 

        fetch_slug = HISTORY_SLUG_OVERRIDES.get(slug, slug)
        url = f"https://api.llama.fi/v2/historicalChainTvl/{fetch_slug}"

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url)
            response.raise_for_status()
            
            try:
                data = response.json()
            except ValueError:
                logger.error(f"DefiLlama API returned non-JSON response for {slug}")
                return 0.0

        if len(data) < 2:
            return 0.0

        unique_data = []
        for entry in reversed(data):
            tvl = entry.get("tvl", 0)
            if not unique_data or unique_data[-1].get("tvl") != tvl:
                unique_data.append(entry)
            if len(unique_data) >= 2:
                break

        if len(unique_data) < 2:
            return 0.0

        latest_tvl = unique_data[0].get("tvl", 0)
        prev_tvl = unique_data[1].get("tvl", 0)

        if prev_tvl > 0:
            change = ((latest_tvl - prev_tvl) / prev_tvl) * 100
            return round(change, 2)

        return 0.0

    except httpx.HTTPError as e:
        logger.error(f"HTTP error fetching historical TVL for {slug} (as {HISTORY_SLUG_OVERRIDES.get(slug, slug)}): {e}")
        return 0.0
    except Exception as e:
        logger.error(f"Error fetching historical TVL for {slug} (as {HISTORY_SLUG_OVERRIDES.get(slug, slug)}): {e}")
        return 0.0


async def get_chains_tvl(detailed_chains: list[str] = None) -> Dict[str, Dict[str, Any]]:
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(DEFILLAMA_CHANS_URL)
            response.raise_for_status()
            data = response.json()

        tvl_map = {}
        for chain in data:
            name = chain.get("name")
            if name:
                tvl_map[name] = {
                    "tvl": chain.get("tvl", 0),
                    "change_1d": chain.get("change_1d", 0),
                    "mcap": chain.get("mcap")
                }

        if detailed_chains:
            logger.info(f"Fetching historical TVL for {len(detailed_chains)} chains")
            tasks = [get_chain_1d_change(name) for name in detailed_chains]
            changes = await asyncio.gather(*tasks)
            for name, change in zip(detailed_chains, changes):
                if name in tvl_map:
                    tvl_map[name]["change_1d"] = change

        return tvl_map

    except Exception as e:
        logger.error(f"Error fetching DefiLlama TVL data: {e}")
        return {}
