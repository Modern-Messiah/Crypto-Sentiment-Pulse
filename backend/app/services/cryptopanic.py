import logging
import httpx
from typing import Optional

from app.core.config import settings

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


def fetch_news_sync() -> list[dict]:
    """
    Synchronous version for Celery tasks.
    """
    import httpx as httpx_sync

    token = settings.CRYPTOPANIC_API_TOKEN
    if not token:
        logger.warning("CRYPTOPANIC_API_TOKEN not set, skipping news fetch")
        return []

    try:
        response = httpx_sync.get(
            CRYPTOPANIC_API_URL,
            params={"auth_token": token},
            timeout=15.0
        )
        response.raise_for_status()
        data = response.json()
        results = data.get("results", [])
        logger.info(f"Fetched {len(results)} news from CryptoPanic (sync)")
        return results

    except Exception as e:
        logger.error(f"CryptoPanic sync fetch error: {e}")
        return []
