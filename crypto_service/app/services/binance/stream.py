import asyncio
import json
import logging
import websockets
from collections import deque, defaultdict

from app.services.binance.history import BinanceHistoryMixin
from app.services.binance.persistence import BinancePersistenceMixin
from app.services.binance.updater import BinanceUpdaterMixin
from app.services.binance.processor import BinanceProcessorMixin

logger = logging.getLogger(__name__)

class BinancePriceStream(
    BinanceHistoryMixin,
    BinancePersistenceMixin,
    BinanceUpdaterMixin,
    BinanceProcessorMixin
):
    def __init__(self, symbols: list[str]):
        self.symbols = [s.lower() for s in symbols]
        self.prices = {}
        self.history = defaultdict(lambda: deque(maxlen=1000))
        self._last_minute_ts = defaultdict(int)
        self.trending_symbols = set()
        self.tvl_data = {}
        self.money_flows = {}
        self.global_stats = {}
        self._running = False
        self._ws = None

    def get_prices(self) -> dict:
        return self.prices

    def get_history(self, symbol: str) -> list:
        if symbol in self.history:
            return list(self.history[symbol])
        return []

    async def start(self, redis_client):
        await self.fetch_initial_history()
        self._running = True

        asyncio.create_task(self._persistence_loop())
        asyncio.create_task(self._trending_update_loop())
        asyncio.create_task(self._defillama_update_loop())
        asyncio.create_task(self._fear_greed_update_loop(redis_client))
        asyncio.create_task(self._redis_publish_loop(redis_client))

        url = "wss://stream.binance.com:9443/ws"
        logger.info(f"Connecting to Binance ({url})...")

        while self._running:
            try:
                async with websockets.connect(url, ping_interval=None) as ws:
                    self._ws = ws
                    logger.info("Connected to Binance! Sending subscription...")

                    params = [f"{s}@ticker" for s in self.symbols]
                    await ws.send(json.dumps({
                        "method": "SUBSCRIBE",
                        "params": params,
                        "id": 1
                    }))

                    while self._running:
                        try:
                            msg = await ws.recv()
                            data = json.loads(msg)
                            await self.process_message(data)

                        except websockets.ConnectionClosed:
                            logger.warning("Binance connection closed, reconnecting...")
                            break
                        except Exception as e:
                            logger.error(f"Error handling Binance message: {e}")
                            break

            except Exception as e:
                logger.error(f"Binance connection error: {e}")
                if self._running:
                    logger.info("Reconnecting to Binance in 5 seconds...")
                    await asyncio.sleep(5)

    async def close(self):
        self._running = False
        if self._ws:
            await self._ws.close()
