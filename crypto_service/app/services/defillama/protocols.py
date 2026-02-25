import logging
from typing import Dict, Any, List

from app.services.defillama.config import DEFILLAMA_PROTOCOLS_URL, create_client

logger = logging.getLogger(__name__)

async def get_protocols_tvl(slugs: List[str]) -> Dict[str, Dict[str, Any]]:
    try:
        async with create_client() as client:
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
