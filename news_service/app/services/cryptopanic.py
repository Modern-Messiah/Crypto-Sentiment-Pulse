import asyncio
import json
import logging

import httpx

from app.core.config import settings
from app.core.celery_app import celery_app

logger = logging.getLogger(__name__)

CRYPTOPANIC_API_URL = "https://cryptopanic.com/api/developer/v2/posts/"


async def fetch_news() -> list[dict]:
    """
    Fetch latest news from CryptoPanic API.
    Returns a list of news dicts or empty list on failure.
    """
    token = settings.CRYPTOPANIC_API_TOKEN
    if not token:
        logger.warning("CRYPTOPANIC_API_TOKEN not set, skipping news fetch")
        return []

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(
                CRYPTOPANIC_API_URL,
                params={"auth_token": token}
            )
            response.raise_for_status()
            data = response.json()
            results = data.get("results", [])
            logger.info(f"Fetched {len(results)} news from CryptoPanic")
            return results

    except httpx.HTTPStatusError as e:
        logger.error(f"CryptoPanic API error: {e.response.status_code} {e.response.text}")
        return []
    except Exception as e:
        logger.error(f"CryptoPanic fetch error: {e}")
        return []


async def cryptopanic_fetch_loop(redis_client):
    """
    Periodically fetch CryptoPanic news, send Celery task
    for DB persistence, and publish to Redis for WebSocket broadcast.
    """
    logger.info(f"Starting CryptoPanic fetch loop (every {settings.CRYPTOPANIC_FETCH_INTERVAL}s)...")

    # Initial fetch on startup
    await _do_fetch_and_publish(redis_client)

    while True:
        try:
            await asyncio.sleep(settings.CRYPTOPANIC_FETCH_INTERVAL)
            await _do_fetch_and_publish(redis_client)
        except asyncio.CancelledError:
            logger.info("CryptoPanic fetch loop cancelled")
            break
        except Exception as e:
            logger.error(f"Error in CryptoPanic fetch loop: {e}")
            await asyncio.sleep(60)


async def _do_fetch_and_publish(redis_client):
    """Fetch news, send Celery task, and publish to Redis."""
    try:
        # Trigger the Celery task (same task the worker already handles)
        celery_app.send_task(
            "app.tasks.cryptopanic_tasks.fetch_and_persist_news"
        )
        logger.info("Sent CryptoPanic fetch task to Celery worker")

        # Also fetch and publish to Redis for real-time WebSocket updates
        news_list = await fetch_news()
        if news_list:
            payload = json.dumps({
                "type": "cryptopanic_update",
                "data": news_list
            }, default=str)
            await redis_client.publish(settings.REDIS_CHANNEL_CRYPTOPANIC, payload)
            logger.info(f"Published {len(news_list)} CryptoPanic news to Redis")

    except Exception as e:
        logger.error(f"Error in CryptoPanic fetch and publish: {e}")
