import json
import logging

from fastapi import APIRouter

import redis.asyncio as aioredis
from app.core.config import settings
from app.core.ws_manager import manager

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/")
async def health_check():
    connected = False
    try:
        r = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
        raw = await r.get("crypto:prices")
        await r.aclose()
        if raw:
            data = json.loads(raw)
            prices = data.get("prices", data)
            connected = len(prices) > 0
    except Exception as e:
        logger.error(f"Health check Redis error: {e}")

    return {
        "status": "healthy" if connected else "connecting",
        "crypto_service_connected": connected,
        "active_websocket_clients": len(manager.active_connections),
    }
