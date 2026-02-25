import asyncio
import json
import logging

import httpx

from app.core.config import settings
from app.core.celery_app import celery_app

logger = logging.getLogger(__name__)

CRYPTOPANIC_API_URL = "https://cryptopanic.com/api/developer/v2/posts/"


async def fetch_news() -> list[dict]:

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

    logger.info(f"Starting CryptoPanic fetch loop (every {settings.CRYPTOPANIC_FETCH_INTERVAL}s)...")

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
    try:
        news_list = await fetch_news()
        if not news_list:
            return

        celery_app.send_task(
            "app.tasks.cryptopanic_tasks.fetch_and_persist_news",
            args=[news_list]
        )
        logger.info(f"Sent {len(news_list)} CryptoPanic news to Celery worker for persistence")

        payload = json.dumps({
            "type": "cryptopanic_update",
            "data": news_list
        }, default=str)
        await redis_client.publish(settings.REDIS_CHANNEL_CRYPTOPANIC, payload)
        logger.info(f"Published {len(news_list)} CryptoPanic news to Redis")

    except Exception as e:
        logger.error(f"Error in CryptoPanic fetch and publish: {e}")
