import asyncio
import json
import logging
import websockets

from collections import deque, defaultdict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BinancePriceStream:
    """Класс для получения live данных от Binance WebSocket"""
    
    def __init__(self, symbols: list[str]):
        self.symbols = [s.lower() for s in symbols]
        self.prices = {}
        # Храним историю: symbol -> deque([(ts, price), ...])
        self.history = defaultdict(lambda: deque(maxlen=100))
        self._running = False
        self._ws = None
        
    async def start(self):
        """Запуск WebSocket потока"""
        self._running = True
        
        # Endpoint for manual subscription
        url = "wss://stream.binance.com:9443/ws"
        
        logger.info(f"Connecting to Binance ({url})...")
        
        while self._running:
            try:
                async with websockets.connect(url, ping_interval=None) as ws:
                    self._ws = ws
                    logger.info("Connected! Sending subscription...")
                    
                    # Manual Subscribe
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
                            logger.error(f"Error handling message: {e}")
                            break
                            
            except Exception as e:
                logger.error(f"Binance connection error: {e}")
                if self._running:
                    logger.info("Reconnecting in 5 seconds...")
                    await asyncio.sleep(5)
    
    async def process_message(self, data: dict):
        """Обработка сообщения"""
        try:
            # Ignore subscription response
            if 'result' in data:
                logger.info("Subscription confirmed")
                return
                
            # Check event type
            # Ticker event usually has "e": "24hrTicker"
            event_type = data.get('e')
            
            if event_type == '24hrTicker':
                symbol = data.get('s')
                if symbol:
                    price = float(data.get('c', 0))
                    timestamp = data.get('E')
                    
                    self.prices[symbol] = {
                        'symbol': symbol,
                        'price': price,
                        'change_24h': float(data.get('P', 0)),
                        'volume_24h': float(data.get('v', 0)),
                        'high_24h': float(data.get('h', 0)),
                        'low_24h': float(data.get('l', 0)),
                        'timestamp': timestamp
                    }
                    
                    # Store in history
                    self.history[symbol].append({
                        'time': timestamp,
                        'price': price
                    })
        except Exception as e:
            logger.error(f"Error processing data: {e}")
    
    def get_prices(self) -> dict:
        return self.prices
        
    def get_history(self, symbol: str) -> list:
        """Returns list of last 100 prices"""
        if symbol in self.history:
            return list(self.history[symbol])
        return []
    
    async def close(self):
        self._running = False
        if self._ws:
            await self._ws.close()

# Global instance
binance_stream: BinancePriceStream | None = None

async def init_binance_stream(symbols: list[str]) -> BinancePriceStream:
    global binance_stream
    binance_stream = BinancePriceStream(symbols)
    asyncio.create_task(binance_stream.start())
    return binance_stream
