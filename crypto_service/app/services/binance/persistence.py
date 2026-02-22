import asyncio
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class BinancePersistenceMixin:

    async def _persistence_loop(self):
        from app.db.session import SessionLocal
        from app.models.price_history import PriceHistory

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
