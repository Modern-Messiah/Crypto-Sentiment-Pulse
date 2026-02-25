import asyncio
import json
import logging

logger = logging.getLogger(__name__)

class BinanceUpdaterMixin:

    async def _trending_update_loop(self):
        from app.services.coingecko import get_trending_symbols

        logger.info("Starting CoinGecko trending update loop (15m)...")
        while self._running:
            try:
                self.trending_symbols = await get_trending_symbols()
                await asyncio.sleep(15 * 60)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in trending update loop: {e}")
                await asyncio.sleep(60)

    async def _coingecko_market_data_loop(self):
        from app.services.coingecko import get_coins_markets_data, COINGECKO_IDS_MAPPING

        logger.info("Starting CoinGecko market data update loop (10m)...")
        while self._running:
            try:
                symbols = list(COINGECKO_IDS_MAPPING.keys())
                self.tvl_data = await get_coins_markets_data(symbols)
                
                self.money_flows = {} 
                self.global_stats = {}

                await asyncio.sleep(10 * 60)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in CoinGecko market data update loop: {e}")
                await asyncio.sleep(60)

    async def _fear_greed_update_loop(self, redis_client):
        from app.services.fear_greed import get_fear_greed_index
        from app.core.config import settings

        logger.info("Starting Fear & Greed update loop (5m)...")
        while self._running:
            try:
                fg_data = await get_fear_greed_index()
                if fg_data:
                    await redis_client.set(settings.REDIS_FEAR_GREED_KEY, json.dumps(fg_data))
                    logger.info(f"Fear & Greed updated: {fg_data.get('value')} ({fg_data.get('value_classification')})")
                await asyncio.sleep(5 * 60)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in Fear & Greed update loop: {e}")
                await asyncio.sleep(60)

    async def _redis_publish_loop(self, redis_client):
        from app.core.config import settings

        logger.info("Starting Redis publish loop (1s)...")
        while self._running:
            try:
                await asyncio.sleep(1)
                if not self.prices:
                    continue

                payload = json.dumps({"prices": self.prices})

                await redis_client.publish(settings.REDIS_CHANNEL, payload)
                await redis_client.set(settings.REDIS_PRICES_KEY, payload)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in Redis publish loop: {e}")
