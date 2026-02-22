import json
import logging

from fastapi import APIRouter

import redis.asyncio as aioredis
from app.core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/")
async def get_prices():
    try:
        r = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
        raw = await r.get("crypto:prices")
        await r.aclose()
        if raw:
            data = json.loads(raw)
            prices = data.get("prices", data)
            return {"data": prices, "count": len(prices)}
    except Exception as e:
        logger.error(f"Error reading prices from Redis: {e}")

    return {"data": {}, "count": 0}
