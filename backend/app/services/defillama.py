import httpx
import logging
import asyncio
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

DEFILLAMA_CHANS_URL = "https://api.llama.fi/chains"
DEFILLAMA_STABLES_URL = "https://stablecoins.llama.fi/stablecoinchains"
DEFILLAMA_PROTOCOLS_URL = "https://api.llama.fi/protocols"

# Some chains have different names in /chains vs /historicalChainTvl
HISTORY_SLUG_OVERRIDES = {
    "Binance": "BSC",
    "Ripple": "XRPL",
    "Cosmos": "CosmosHub",
    "Near": "near"
}

async def get_chain_1d_change(slug: str, is_protocol: bool = False) -> float:
    """
    Fetch historical TVL for a chain or protocol and calculate 1d change.
    """
    try:
        # Apply slug overrides for history endpoint
        fetch_slug = HISTORY_SLUG_OVERRIDES.get(slug, slug)
        
        if is_protocol:
            return 0.0 # Placeholder
            
        url = f"https://api.llama.fi/v2/historicalChainTvl/{fetch_slug}"
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()
            if len(data) >= 2:
                latest_tvl = data[-1].get("tvl", 0)
                prev_tvl = data[-2].get("tvl", 0)
                if prev_tvl > 0:
                    change = ((latest_tvl - prev_tvl) / prev_tvl) * 100
                    return round(change, 2)
            return 0.0
    except Exception as e:
        logger.error(f"Error fetching historical TVL for {slug} (as {fetch_slug}): {e}")
        return 0.0

async def get_protocols_tvl(slugs: List[str]) -> Dict[str, Dict[str, Any]]:
    """
    Fetch TVL for specific protocols (Uniswap, Lido, etc.)
    """
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(DEFILLAMA_PROTOCOLS_URL)
            response.raise_for_status()
            data = response.json()
            
            proto_map = {}
            target_slugs = set(slugs)
            
            for p in data:
                slug = p.get("slug")
                if slug in target_slugs:
                    logger.info(f"Found protocol data for slug: {slug}")
                    proto_map[slug] = {
                        "tvl": p.get("tvl", 0),
                        "change_1d": p.get("change_1d", 0),
                        "mcap": p.get("mcap", 0)
                    }
            return proto_map
    except Exception as e:
        logger.error(f"Error fetching DefiLlama protocols: {e}")
        return {}

async def get_chains_tvl(detailed_chains: list[str] = None) -> Dict[str, Dict[str, Any]]:
    """
    Fetch TVL for all chains from DefiLlama.
    If detailed_chains is provided, will also fetch historical 1d change for those chains.
    """
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
                        "change_1d": 0.0,
                        "mcap": chain.get("mcap")
                    }
            
            if detailed_chains:
                logger.info(f"Fetching historical TVL for {len(detailed_chains)} chains")
                # Note: get_chain_1d_change will use HISTORY_SLUG_OVERRIDES internally
                tasks = [get_chain_1d_change(name) for name in detailed_chains]
                changes = await asyncio.gather(*tasks)
                for name, change in zip(detailed_chains, changes):
                    if name in tvl_map:
                        tvl_map[name]["change_1d"] = change
            
            return tvl_map
    except Exception as e:
        logger.error(f"Error fetching DefiLlama TVL data: {e}")
        return {}

async def get_stablecoin_flows() -> Dict[str, Dict[str, Any]]:
    """
    Fetch stablecoin net flows for all chains.
    """
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(DEFILLAMA_STABLES_URL)
            response.raise_for_status()
            data = response.json()
            
            flow_map = {}
            for chain in data:
                name = chain.get("name")
                if name:
                    flow_map[name] = {
                        "mcap": chain.get("totalCirculating", {}).get("peggedUSD", 0),
                        "net_change_1d": chain.get("circulatingPrevDay", {}).get("peggedUSD", 0) # This needs better calculation
                    }
                    # DefiLlama stablecoins API often lists net change directly in some fields or we calculate:
                    # current - prev
                    current = chain.get("totalCirculating", {}).get("peggedUSD", 0)
                    prev = chain.get("circulatingPrevDay", {}).get("peggedUSD", 0)
                    flow_map[name]["net_flow_1d"] = current - prev
            
            return flow_map
    except Exception as e:
        logger.error(f"Error fetching stablecoin flows: {e}")
        return {}

async def get_global_stats() -> Dict[str, Any]:
    """
    Get global DeFi metrics.
    """
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            # We can get total TVL from chains
            tvl_data = await get_chains_tvl()
            total_tvl = sum(c["tvl"] for c in tvl_data.values())
            
            return {
                "total_tvl": total_tvl,
                "chain_count": len(tvl_data)
            }
    except Exception as e:
        logger.error(f"Error getting global stats: {e}")
        return {}
