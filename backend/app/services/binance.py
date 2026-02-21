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
        self._last_minute_ts = defaultdict(int) # Track last minute timestamp for RSI candle closure
        self.trending_symbols = set()
        self.tvl_data = {}
        self.money_flows = {}
        self.global_stats = {}
        self._running = False
        self._ws = None
        
    async def fetch_initial_history(self):
        import requests
        from app.db.session import SessionLocal
        from app.models.price_history import PriceHistory
        from datetime import datetime, timezone, timedelta
        
        logger.info("Fetching high-res initial history for all symbols (1m + 5m backfill)...")
        tasks = []
        for symbol in self.symbols:
            # Fetch 60 candles of 1m = 1 hour high-res
            tasks.append(self._fetch_and_persist(symbol.upper(), "1m", 60))
            # Fetch 288 candles of 5m = 24 hours
            tasks.append(self._fetch_and_persist(symbol.upper(), "5m", 288))
        
        await asyncio.gather(*tasks)
        logger.info("High-res history fetching completed.")
        
        # Pre-populate RSI history from DB
        db = SessionLocal()
        try:
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

    async def _fetch_and_persist(self, symbol_upper, interval, limit):
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
                    await asyncio.to_thread(self._bulk_save_history, new_entries, symbol_upper)
        except Exception as e:
            logger.error(f"Failed to fetch {interval} history for {symbol_upper}: {e}")

    def _bulk_save_history(self, entries, symbol):
        from app.models.price_history import PriceHistory
        from datetime import datetime, timedelta
        
        from app.db.session import SessionLocal
        db = SessionLocal()
        try:
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
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to bulk save history for {symbol}: {e}")
        finally:
            db.close()

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
                    db.rollback()
                    logger.error(f"Error in persistence loop: {e}")
                finally:
                    db.close()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Extreme error in persistence loop: {e}")

    async def _trending_update_loop(self):
        from app.services.coingecko import get_trending_symbols
        
        logger.info("Starting CoinGecko trending update loop (15m)...")
        while self._running:
            try:
                self.trending_symbols = await get_trending_symbols()
                # Wait for 15 minutes before next update
                await asyncio.sleep(15 * 60)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in trending update loop: {e}")
                await asyncio.sleep(60)

    async def _defillama_update_loop(self):
        from app.services.defillama import get_chains_tvl, get_stablecoin_flows, get_global_stats, get_protocols_tvl
        
        # Tracked chains for detailed TVL change calculation
        detailed_chains = [
            "Bitcoin", "Ethereum", "Solana", "Binance", "Arbitrum", "Optimism", 
            "Polygon", "Avalanche", "Tron", "Cardano", "Polkadot", "Near",
            "Ripple", "Stellar", "Cosmos", "Filecoin", "Litecoin", "Doge", "EthereumClassic"
        ]
        # Tracked protocols (for coins that are primary protocols)
        tracked_protocols = ["lido", "uniswap-v3", "aave-v3", "stake.link-liquid"]
        
        logger.info("Starting DefiLlama update loop (5m)...")
        while self._running:
            try:
                # Fetch chains TVL first
                self.tvl_data = await get_chains_tvl(detailed_chains=detailed_chains)
                
                # Fetch protocols, money flows, and global stats
                proto_data, self.money_flows, self.global_stats = await asyncio.gather(
                    get_protocols_tvl(tracked_protocols),
                    get_stablecoin_flows(),
                    get_global_stats()
                )
                
                # Merge protocol data into tvl_data using their slugs as keys
                for slug, data in proto_data.items():
                    logger.info(f"Merging protocol data into tvl_data: {slug}")
                    self.tvl_data[slug] = data
                
                # Wait for 5 minutes before next update
                await asyncio.sleep(5 * 60)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in DefiLlama update loop: {e}")
                await asyncio.sleep(60)

    async def process_message(self, data: dict):
        # Mapping for TVL (Chain name or Protocol slug from DefiLlama)
        MAPPING = {
            'BTCUSDT': 'Bitcoin',
            'ETHUSDT': 'Ethereum',
            'SOLUSDT': 'Solana',
            'BNBUSDT': 'Binance',
            'ARBUSDT': 'Arbitrum',
            'OPUSDT': 'Optimism',
            'POLUSDT': 'Polygon',
            'AVAXUSDT': 'Avalanche',
            'TRXUSDT': 'Tron',
            'ADAUSDT': 'Cardano',
            'DOTUSDT': 'Polkadot',
            'NEARUSDT': 'Near',
            'AAVEUSDT': 'aave-v3',
            'UNIUSDT': 'uniswap-v3',
            'LINKUSDT': 'stake.link-liquid',
            'ATOMUSDT': 'Cosmos',
            'FILUSDT': 'Filecoin',
            'LTCUSDT': 'Litecoin',
            'XLMUSDT': 'Stellar', 
            'XRPUSDT': 'Ripple',
            'DOGEUSDT': 'Doge',
            'ETCUSDT': 'EthereumClassic'
        }
        
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
                    
                    # Manage RSI... (rest of the logic remains)
                    history_prices = [p['price'] for p in self.history[symbol]]
                    history_times = [p['time'] for p in self.history[symbol]]
                    
                    if not history_prices:
                        rsi = 50.0
                    else:
                        minute_closes = []
                        seen_minutes = set()
                        
                        for t, p in zip(reversed(history_times), reversed(history_prices)):
                            minute_key = int(t / 60000)
                            if minute_key not in seen_minutes:
                                minute_closes.append(p)
                                seen_minutes.add(minute_key)
                                if len(minute_closes) >= 15:
                                    break
                        
                        minute_closes.reverse()
                        
                        if len(minute_closes) < 15 and len(history_prices) > 20:
                            sample_prices = history_prices[::5]
                            rsi = self.calculate_rsi(sample_prices, period=14)
                        elif len(minute_closes) >= 15:
                            rsi = self.calculate_rsi(minute_closes, period=14)
                        else:
                            rsi = 50.0

                    # Check trending status
                    is_trending = False
                    for trending in self.trending_symbols:
                        if trending in symbol:
                            is_trending = True
                            break

                    # Get TVL and Money Flow data if available
                    tvl_key = MAPPING.get(symbol)
                    tvl_info = self.tvl_data.get(tvl_key) if tvl_key else None
                    flow_info = self.money_flows.get(tvl_key) if tvl_key else None

                    self.prices[symbol] = {
                        'symbol': symbol,
                        'price': price,
                        'change_24h': float(data.get('P', 0)),
                        'volume_24h': float(data.get('v', 0)),
                        'high_24h': float(data.get('h', 0)),
                        'low_24h': float(data.get('l', 0)),
                        'timestamp': timestamp,
                        'rsi': rsi,
                        'is_trending': is_trending,
                        'tvl': tvl_info.get('tvl') if tvl_info else None,
                        'tvl_change_1d': tvl_info.get('change_1d') if tvl_info else None,
                        'money_flow_24h': flow_info.get('net_flow_1d') if flow_info else None,
                        'global_stats': self.global_stats
                    }
                    
        except Exception as e:
            logger.error(f"Error processing Binance data: {e}")

    def calculate_rsi(self, prices, period=14):
        if len(prices) < period + 1:
            return 50.0
        
        gains = []
        losses = []
        
        for i in range(1, len(prices)):
            change = prices[i] - prices[i-1]
            if change > 0:
                gains.append(change)
                losses.append(0)
            else:
                gains.append(0)
                losses.append(abs(change))
        
        recent_gains = gains[-period:]
        recent_losses = losses[-period:]
        
        avg_gain = sum(recent_gains) / period
        avg_loss = sum(recent_losses) / period
        
        if avg_loss == 0:
            return 100.0 if avg_gain > 0 else 50.0
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return round(rsi, 1)

    def get_prices(self) -> dict:
        return self.prices
        
    def get_history(self, symbol: str) -> list:
        if symbol in self.history:
            return list(self.history[symbol])
        return []

    async def start(self):
        await self.fetch_initial_history()
        self._running = True
        
        asyncio.create_task(self._persistence_loop())
        # Start trending loop
        asyncio.create_task(self._trending_update_loop())
        # Start DefiLlama loop
        asyncio.create_task(self._defillama_update_loop())
        
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

binance_stream: BinancePriceStream | None = None

async def init_binance_stream(symbols: list[str]) -> BinancePriceStream:
    global binance_stream
    binance_stream = BinancePriceStream(symbols)
    asyncio.create_task(binance_stream.start())
    return binance_stream
