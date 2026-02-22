import asyncio
import logging
import redis.asyncio as aioredis

from app.core.config import settings
from app.services.binance import BinancePriceStream

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
)
logger = logging.getLogger("crypto_service")


async def main():
    logger.info("=" * 60)
    logger.info("Crypto Service starting...")
    logger.info(f"Tracking {len(settings.TRACKED_SYMBOLS)} symbols")
    logger.info(f"Redis: {settings.REDIS_URL}")
    logger.info("=" * 60)

    redis_client = aioredis.from_url(settings.REDIS_URL, decode_responses=True)

    try:
        await redis_client.ping()
        logger.info("Connected to Redis successfully")
    except Exception as e:
        logger.error(f"Failed to connect to Redis: {e}")
        raise

    stream = BinancePriceStream(settings.TRACKED_SYMBOLS)

    try:
        await stream.start(redis_client)
    except KeyboardInterrupt:
        logger.info("Shutting down...")
    finally:
        await stream.close()
        await redis_client.aclose()
        logger.info("Crypto Service shutdown complete")


if __name__ == "__main__":
    asyncio.run(main())
