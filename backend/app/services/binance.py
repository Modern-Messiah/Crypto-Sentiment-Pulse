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
        self.history = defaultdict(lambda: deque(maxlen=1000))
        self._running = False
        self._ws = None
        
    async def fetch_initial_history(self):
        import requests
        from app.db.session import SessionLocal
        from app.models.price_history import PriceHistory
        from datetime import datetime, timezone, timedelta
        
        logger.info("Fetching high-res initial history for all symbols (1m + 5m backfill)...")
        db = SessionLocal()
        try:
            tasks = []
            for symbol in self.symbols:
                # Fetch 60 candles of 1m = 1 hour high-res
                tasks.append(self._fetch_and_persist(db, symbol.upper(), "1m", 60))
                # Fetch 288 candles of 5m = 24 hours
                tasks.append(self._fetch_and_persist(db, symbol.upper(), "5m", 288))
            
            await asyncio.gather(*tasks)
            logger.info("High-res history fetching completed.")
            
            # Pre-populate RSI history from DB
            # We need the last 20-30 1m closing prices to have an immediate RSI.
            for symbol in self.symbols:
                s_upper = symbol.upper()
                # Get last 50 entries
                history_items = db.query(PriceHistory).filter(
                    PriceHistory.symbol == s_upper
                ).order_by(PriceHistory.timestamp.desc()).limit(50).all()
                
                # Sort ascending by time
                history_items.reverse()
                
                for item in history_items:
                     self.history[s_upper].append({
                        'time': item.timestamp.replace(tzinfo=timezone.utc).timestamp() * 1000,
                        'price': item.price
                     })
                
                self._last_minute_ts[s_upper] = 0
                
        finally:
            db.close()

    def __init__(self, symbols: list[str]):
        self.symbols = [s.lower() for s in symbols]
        self.prices = {}
        self.history = defaultdict(lambda: deque(maxlen=1000))
        self._last_minute_ts = defaultdict(int) # Track last minute timestamp for RSI candle closure
        self._running = False
        self._ws = None

    # ... (rest of methods) ...

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
                    timestamp = data.get('E') # Event time in ms
                    
                    self.history[symbol].append({
                        'time': timestamp,
                        'price': price
                    })
                    
                    # Manage RSI with 1-minute 'candles' logic
                    # We check if we crossed a minute boundary to "close" a candle for RSI
                    # This is better than random sampling.
                    # Or simpler: just use the last 14 * 60 seconds of data?
                    # Let's use a robust approach: Resample history to 1m intervals
                    
                    history_prices = [p['price'] for p in self.history[symbol]]
                    history_times = [p['time'] for p in self.history[symbol]]
                    
                    if not history_prices:
                        rsi = 50.0
                    else:
                         # Simple resampling: Take the last price of each distinct minute
                        minute_closes = []
                        seen_minutes = set()
                        
                        # Iterate backwards
                        for t, p in zip(reversed(history_times), reversed(history_prices)):
                            # t is ms
                            minute_key = int(t / 60000)
                            if minute_key not in seen_minutes:
                                minute_closes.append(p)
                                seen_minutes.add(minute_key)
                                if len(minute_closes) >= 15: # We need 14 periods + 1
                                    break
                        
                        # Reverse back to chronological order
                        minute_closes.reverse()
                        
                        rsi = self.calculate_rsi(minute_closes, period=14)

                    self.prices[symbol] = {
                        'symbol': symbol,
                        'price': price,
                        'change_24h': float(data.get('P', 0)),
                        'volume_24h': float(data.get('v', 0)),
                        'high_24h': float(data.get('h', 0)),
                        'low_24h': float(data.get('l', 0)),
                        'timestamp': timestamp,
                        'rsi': rsi
                    }
                    
        except Exception as e:
            logger.error(f"Error processing Binance data: {e}") 
     
    def get_prices(self) -> dict:
        return self.prices
        
    def get_history(self, symbol: str) -> list:
        if symbol in self.history:
            return list(self.history[symbol])
        return []

    async def _fetch_and_persist(self, db, symbol_upper, interval, limit):
        import requests
        from app.models.price_history import PriceHistory
        from datetime import datetime, timezone
        
        try:
            url = f"https://api.binance.com/api/v3/klines?symbol={symbol_upper}&interval={interval}&limit={limit}"
            response = await asyncio.to_thread(requests.get, url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                new_entries = []
                for kline in data:
                    ts_ms = kline[0]
                    price = float(kline[4])
                    dt = datetime.fromtimestamp(ts_ms / 1000, tz=timezone.utc).replace(tzinfo=None)
                    
                    new_entries.append(PriceHistory(
                        symbol=symbol_upper,
                        price=price,
                        timestamp=dt
                    ))
                
                if new_entries:
                    await asyncio.to_thread(self._bulk_save_history, db, new_entries, symbol_upper)
        except Exception as e:
            logger.error(f"Failed to fetch {interval} history for {symbol_upper}: {e}")

    def _bulk_save_history(self, db, entries, symbol):
        from app.models.price_history import PriceHistory
        from datetime import datetime, timedelta
        
        # Check existing timestamps to avoid exact duplicates
        since = min(e.timestamp for e in entries) - timedelta(minutes=1)
        existing_ts = db.query(PriceHistory.timestamp).filter(
            PriceHistory.symbol == symbol,
            PriceHistory.timestamp >= since
        ).all()
        existing_set = {t[0] for t in existing_ts}
        
        to_insert = [e for e in entries if e.timestamp not in existing_set]
        if to_insert:
            db.bulk_save_objects(to_insert)
            db.commit()
            logger.info(f"Backfilled {len(to_insert)} new points for {symbol}")

    async def _persistence_loop(self):
        from app.db.session import SessionLocal
        from app.models.price_history import PriceHistory
        from datetime import datetime
        
        logger.info("Starting real-time persistence loop (5s)...")
        while self._running:
            try:
                await asyncio.sleep(5)
                if not self.prices:
                    continue
                    
                db = SessionLocal()
                try:
                    new_entries = []
                    now = datetime.utcnow()
                    for symbol, data in self.prices.items():
                        new_entries.append(PriceHistory(
                            symbol=symbol.upper(),
                            price=data['price'],
                            timestamp=now
                        ))
                    
                    if new_entries:
                        db.bulk_save_objects(new_entries)
                        db.commit()
                        logger.debug(f"Persisted {len(new_entries)} symbols to DB")
                except Exception as e:
                    logger.error(f"Error in persistence loop: {e}")
                finally:
                    db.close()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Extreme error in persistence loop: {e}")

    async def start(self):
        await self.fetch_initial_history()
        self._running = True
        
        # Start persistence loop
        asyncio.create_task(self._persistence_loop())
        
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
    
    def calculate_rsi(self, prices, period=14):
        if len(prices) < period + 1:
            return 50.0  # Default neutral
        
        gains = []
        losses = []
        
        # Calculate changes
        for i in range(1, len(prices)):
            change = prices[i] - prices[i-1]
            if change > 0:
                gains.append(change)
                losses.append(0)
            else:
                gains.append(0)
                losses.append(abs(change))
        
        # Simple RSI (standard is EMA, but SMA is faster for streaming approximation)
        # We'll use a simple SMA for the recent period to be fast
        # Better: Wilder's Smoothing if we had a state, but SMA is acceptable for this use case
        recent_gains = gains[-period:]
        recent_losses = losses[-period:]
        
        avg_gain = sum(recent_gains) / period
        avg_loss = sum(recent_losses) / period
        
        if avg_loss == 0:
            return 100.0
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return round(rsi, 1)

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
                    
                    # Update history deque for RSI calculation
                    # We need closing prices. The stream sends 24hrTicker stats constantly.
                    # Ideally we'd use kline stream, but we can approximate by storing price points
                    # if they are new or every X seconds.
                    # Since we only have 'history' deque from 24hrTicker updates (which update every 1s),
                    # we can use that history.
                    
                    self.history[symbol].append({
                        'time': timestamp,
                        'price': price
                    })
                    
                    # Calculate RSI based on the last 50 points (assuming ~1s updates)
                    # This is "Instant RSI" based on tick data, might be noisy but realtime.
                    # For better RSI we need Klines (1m candles).
                    # But user wants "visual level", so tick-based "momentum" is actually cool.
                    
                    history_prices = [p['price'] for p in self.history[symbol]]
                    # Downsample to get meaningful changes if updates are too frequent
                    # Take every 5th point to simulate a "period"
                    if len(history_prices) > 20:
                        sample_prices = history_prices[::5] # subsample
                        rsi = self.calculate_rsi(sample_prices, period=14)
                    else:
                        rsi = 50.0

                    self.prices[symbol] = {
                        'symbol': symbol,
                        'price': price,
                        'change_24h': float(data.get('P', 0)),
                        'volume_24h': float(data.get('v', 0)),
                        'high_24h': float(data.get('h', 0)),
                        'low_24h': float(data.get('l', 0)),
                        'timestamp': timestamp,
                        'rsi': rsi
                    }
                    
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
