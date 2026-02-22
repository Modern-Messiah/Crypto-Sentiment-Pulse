import asyncio
import logging
from datetime import datetime, timezone, timedelta

logger = logging.getLogger(__name__)

class BinanceHistoryMixin:
    
    async def fetch_initial_history(self):
        import requests
        from app.db.session import SessionLocal
        from app.models.price_history import PriceHistory

        logger.info("Fetching high-res initial history for all symbols (1m + 5m backfill)...")
        tasks = []
        for symbol in self.symbols:
            tasks.append(self._fetch_and_persist(symbol.upper(), "1m", 60))
            tasks.append(self._fetch_and_persist(symbol.upper(), "5m", 288))

        await asyncio.gather(*tasks)
        logger.info("High-res history fetching completed.")

        db = SessionLocal()
        try:
            for symbol in self.symbols:
                s_upper = symbol.upper()
                history_items = db.query(PriceHistory).filter(
                    PriceHistory.symbol == s_upper
                ).order_by(PriceHistory.timestamp.desc()).limit(50).all()

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
        from app.db.session import SessionLocal
        from app.models.price_history import PriceHistory

        db = SessionLocal()
        try:
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
                logger.debug(f"Backfilled {len(to_insert)} new points for {symbol}")
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to bulk save history for {symbol}: {e}")
        finally:
            db.close()
