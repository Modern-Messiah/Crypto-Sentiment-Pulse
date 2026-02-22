import logging
from typing import Dict, Any

from app.services.defillama.chains import get_chains_tvl

logger = logging.getLogger(__name__)

async def get_global_stats(tvl_data: Dict[str, Dict[str, Any]] = None) -> Dict[str, Any]:
    try:
        if tvl_data is None:
            tvl_data = await get_chains_tvl()

        total_tvl = sum(c["tvl"] for c in tvl_data.values())

        return {
            "total_tvl": total_tvl,
            "chain_count": len(tvl_data)
        }

    except Exception as e:
        logger.error(f"Error getting global stats: {e}")
        return {}
