import asyncio
import logging
import redis.asyncio as aioredis

from app.config import REDIS_URL, TRACKED_SYMBOLS
from app.services.binance import BinancePriceStream

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
)
logger = logging.getLogger("crypto_service")


async def main():
    logger.info("=" * 60)
    logger.info("Crypto Service starting...")
    logger.info(f"Tracking {len(TRACKED_SYMBOLS)} symbols")
    logger.info(f"Redis: {REDIS_URL}")
    logger.info("=" * 60)

    # Connect to Redis (async)
    redis_client = aioredis.from_url(REDIS_URL, decode_responses=True)

    try:
        await redis_client.ping()
        logger.info("Connected to Redis successfully")
    except Exception as e:
        logger.error(f"Failed to connect to Redis: {e}")
        raise

    # Start Binance stream (this blocks forever internally)
    stream = BinancePriceStream(TRACKED_SYMBOLS)

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
