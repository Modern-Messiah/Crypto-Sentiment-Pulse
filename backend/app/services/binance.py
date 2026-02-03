import asyncio
import json
import logging
import websockets
from collections import deque, defaultdict

logger = logging.getLogger(__name__)

class BinancePriceStream:
    
    def __init__(self, symbols: list[str]):
        self.symbols = [s.lower() for s in symbols]
        self.prices = {}
        self.history = defaultdict(lambda: deque(maxlen=100))
        self._running = False
        self._ws = None
        
    async def fetch_initial_history(self):
        import requests
        
        logger.info("Fetching initial history for all symbols...")
        for symbol in self.symbols:
            try:
                # Binance klines API (1m interval)
                symbol_upper = symbol.upper()
                url = f"https://api.binance.com/api/v3/klines?symbol={symbol_upper}&interval=1m&limit=100"
                
                response = await asyncio.to_thread(requests.get, url, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    for kline in data:
                        timestamp = kline[0]
                        price = float(kline[4])
                        self.history[symbol_upper].append({
                            'time': timestamp,
                            'price': price
                        })
                logger.info(f"Initialized history for {symbol_upper} ({len(self.history[symbol_upper])} points)")
            except Exception as e:
                logger.error(f"Failed to fetch initial history for {symbol}: {e}")

    async def start(self):
        await self.fetch_initial_history()
        self._running = True
        
        url = "wss://stream.binance.com:9443/ws"
        
        logger.info(f"Connecting to Binance ({url})...")
        
        while self._running:
            try:
                async with websockets.connect(url, ping_interval=None) as ws:
                    self._ws = ws
                    logger.info("Connected to Binance! Sending subscription...")
                    
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
                            logger.error(f"Error handling Binance message: {e}")
                            break
                            
            except Exception as e:
                logger.error(f"Binance connection error: {e}")
                if self._running:
                    logger.info("Reconnecting to Binance in 5 seconds...")
                    await asyncio.sleep(5)
    
    async def process_message(self, data: dict):
        try:
            if 'result' in data:
                logger.info("Binance subscription confirmed")
                return
                
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
                    
                    self.history[symbol].append({
                        'time': timestamp,
                        'price': price
                    })
        except Exception as e:
            logger.error(f"Error processing Binance data: {e}")
    
    def get_prices(self) -> dict:
        return self.prices
        
    def get_history(self, symbol: str) -> list:
        if symbol in self.history:
            return list(self.history[symbol])
        return []
    
    async def close(self):
        self._running = False
        if self._ws:
            await self._ws.close()

binance_stream: BinancePriceStream | None = None

async def init_binance_stream(symbols: list[str]) -> BinancePriceStream:
    global binance_stream
    binance_stream = BinancePriceStream(symbols)
    asyncio.create_task(binance_stream.start())
    return binance_stream
