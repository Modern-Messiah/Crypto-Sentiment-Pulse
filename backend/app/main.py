import asyncio
import json
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from app.api.api_v1.api import api_router
from app.core.config import settings
from app.core.ws_manager import manager
from app.db.session import engine
from app.db.base import Base
from fastapi.staticfiles import StaticFiles
import os

import redis.asyncio as aioredis

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Shared state: latest prices from crypto_service via Redis
_latest_prices = {}


def get_latest_prices() -> dict:
    """Get latest prices received from crypto_service via Redis."""
    return _latest_prices


async def _redis_subscriber():
    """Subscribe to Redis Pub/Sub channels and broadcast updates to WebSocket clients."""
    global _latest_prices
    redis_client = aioredis.from_url(settings.REDIS_URL, decode_responses=True)

    channels = ["crypto:updates", "news:telegram", "news:cryptopanic"]

    while True:
        try:
            pubsub = redis_client.pubsub()
            await pubsub.subscribe(*channels)
            logger.info(f"Subscribed to Redis channels: {channels}")

            async for message in pubsub.listen():
                if message["type"] == "message":
                    try:
                        data = json.loads(message["data"])
                        channel = message["channel"]

                        if channel == "crypto:updates":
                            _latest_prices = data.get("prices", {})
                            await manager.broadcast({"type": "update", "data": data})
                        elif channel == "news:telegram":
                            await manager.broadcast(data)
                        elif channel == "news:cryptopanic":
                            await manager.broadcast(data)

                    except (json.JSONDecodeError, Exception) as e:
                        logger.error(f"Error processing Redis message: {e}")

        except asyncio.CancelledError:
            logger.info("Redis subscriber cancelled")
            await pubsub.unsubscribe(*channels)
            await redis_client.aclose()
            return
        except Exception as e:
            logger.error(f"Redis subscriber error: {e}, reconnecting in 3s...")
            await asyncio.sleep(3)


@asynccontextmanager
async def lifespan(app: FastAPI):

    from app.models.cryptopanic_news import CryptoPanicNews  # noqa: ensure table is created
    Base.metadata.create_all(bind=engine)

    # Start Redis subscriber for crypto_service + news_service updates
    redis_task = asyncio.create_task(_redis_subscriber())
    logger.info("Redis subscriber started — listening for crypto:updates, news:telegram, news:cryptopanic")

    yield

    redis_task.cancel()
    try:
        await redis_task
    except asyncio.CancelledError:
        pass

    logger.info("Backend shutdown complete")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure media directory exists
media_path = "/data/media"
if not os.path.exists(media_path):
    os.makedirs(media_path, exist_ok=True)
    logger.info(f"Created media directory: {media_path}")

app.mount("/media", StaticFiles(directory=media_path), name="media")

@app.get("/")
def root():
    """API info"""
    return {
        "message": settings.PROJECT_NAME,
        "version": "1.0.0",
        "tracked_symbols": settings.TRACKED_SYMBOLS,
        "telegram_channels": settings.TELEGRAM_CHANNELS,
    }

app.include_router(api_router, prefix=settings.API_V1_STR)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)

    try:
        while True:
            # Keep connection alive; data is pushed via Redis subscriber broadcast
            await asyncio.sleep(30)
            # Send ping/keepalive
            try:
                await websocket.send_json({"type": "ping"})
            except Exception:
                break

    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}", exc_info=True)
        manager.disconnect(websocket)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
