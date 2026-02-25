import json
import logging

from fastapi import APIRouter

import redis.asyncio as aioredis
from app.core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/fear-greed")
async def read_fear_greed():
    try:
        r = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
        raw = await r.get("crypto:fear_greed")
        await r.aclose()
        if raw:
            return json.loads(raw)
    except Exception as e:
        logger.error(f"Error reading Fear & Greed from Redis: {e}")

    return {
        "value": 50,
        "value_classification": "Neutral",
        "timestamp": None,
        "error": "Data not yet available from crypto_service"
    }
