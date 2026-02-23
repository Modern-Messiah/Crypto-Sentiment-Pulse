import asyncio
import logging

import redis.asyncio as aioredis

from app.core.config import settings
from app.services.telegram import TelegramService
from app.services.cryptopanic import cryptopanic_fetch_loop

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
)
logger = logging.getLogger("news_service")


async def main():
    logger.info("=" * 60)
    logger.info("News Service starting...")
    logger.info(f"Telegram channels: {len(settings.TELEGRAM_CHANNELS)}")
    logger.info(f"CryptoPanic token: {'set' if settings.CRYPTOPANIC_API_TOKEN else 'not set'}")
    logger.info(f"Redis: {settings.REDIS_URL}")
    logger.info("=" * 60)

    # Connect to Redis
    redis_client = aioredis.from_url(settings.REDIS_URL, decode_responses=True)

    try:
        await redis_client.ping()
        logger.info("Connected to Redis successfully")
    except Exception as e:
        logger.error(f"Failed to connect to Redis: {e}")
        raise

    # Start Telegram service
    tg_service = TelegramService(
        api_id=settings.TELEGRAM_API_ID,
        api_hash=settings.TELEGRAM_API_HASH,
        session_name=settings.TELEGRAM_SESSION_NAME,
    )
    await tg_service.start(settings.TELEGRAM_CHANNELS, redis_client)
    logger.info(f"Telegram service started. Monitoring {len(settings.TELEGRAM_CHANNELS)} channels")

    # Start CryptoPanic fetch loop
    cryptopanic_task = asyncio.create_task(cryptopanic_fetch_loop(redis_client))
    logger.info("CryptoPanic fetch loop started")

    logger.info("=" * 60)
    logger.info("News Service is fully running!")
    logger.info("=" * 60)

    try:
        # Keep running forever
        await asyncio.Event().wait()
    except (KeyboardInterrupt, asyncio.CancelledError):
        logger.info("Shutting down...")
    finally:
        cryptopanic_task.cancel()
        try:
            await cryptopanic_task
        except asyncio.CancelledError:
            pass

        await tg_service.close()
        await redis_client.aclose()
        logger.info("News Service shutdown complete")


if __name__ == "__main__":
    asyncio.run(main())
