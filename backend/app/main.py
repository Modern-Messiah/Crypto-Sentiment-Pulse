import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from app.api.api_v1.api import api_router
from app.core.config import settings
from app.core.ws_manager import manager
from app.services import binance as bs
from app.services import telegram as tg
from app.db.session import engine
from app.db.base import Base
from fastapi.staticfiles import StaticFiles
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):

    from app.models.cryptopanic_news import CryptoPanicNews  # noqa: ensure table is created
    Base.metadata.create_all(bind=engine)
    
    await bs.init_binance_stream(settings.TRACKED_SYMBOLS)
    logger.info(f"Backend started. Tracking {len(settings.TRACKED_SYMBOLS)} symbols")
    
    tg_service = await tg.init_telegram_service(
        api_id=settings.TELEGRAM_API_ID,
        api_hash=settings.TELEGRAM_API_HASH,
        session_name=settings.TELEGRAM_SESSION_NAME,
        channels=settings.TELEGRAM_CHANNELS
    )
    
    async def on_telegram_message(msg):
        logger.info(f"Broadcasting telegram_update to {len(manager.active_connections)} clients")
        await manager.broadcast({"type": "telegram_update", "data": msg})
    
    tg_service.set_message_callback(on_telegram_message)
    
    logger.info(f"Telegram service started. Monitoring {len(settings.TELEGRAM_CHANNELS)} channels")

    # Initial CryptoPanic news fetch if DB is empty
    from app.db.session import SessionLocal
    from app.services import cryptopanic as cp
    from datetime import datetime

    db_check = SessionLocal()
    try:
        news_count = db_check.query(CryptoPanicNews).count()
        if news_count == 0 and settings.CRYPTOPANIC_API_TOKEN:
            logger.info("No CryptoPanic news in DB, fetching initial batch...")
            news_list = await cp.fetch_news()
            for item in news_list:
                title = item.get("title", "").strip()
                published_str = item.get("published_at")
                if not title or not published_str:
                    continue
                try:
                    published_at = datetime.fromisoformat(published_str.replace("Z", "+00:00"))
                except (ValueError, TypeError):
                    published_at = datetime.utcnow()

                existing = db_check.query(CryptoPanicNews).filter(
                    CryptoPanicNews.title == title,
                    CryptoPanicNews.published_at == published_at
                ).first()
                if not existing:
                    news = CryptoPanicNews(
                        title=title,
                        description=item.get("description"),
                        published_at=published_at,
                        kind=item.get("kind", "news"),
                        source_title=item.get("source", {}).get("title") if isinstance(item.get("source"), dict) else None,
                        url=item.get("url"),
                    )
                    db_check.add(news)
            db_check.commit()
            logger.info(f"Initial CryptoPanic news loaded: {len(news_list)} items")
        else:
            logger.info(f"CryptoPanic news in DB: {news_count} items, skipping initial fetch")
    except Exception as e:
        logger.error(f"Error during initial CryptoPanic fetch: {e}")
        db_check.rollback()
    finally:
        db_check.close()

    yield

    if bs.binance_stream:
        await bs.binance_stream.close()
    if tg.telegram_service:
        await tg.telegram_service.close()
    logger.info("Backend shutdown complete")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve media files
media_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "media")
if not os.path.exists(media_path):
    os.makedirs(media_path, exist_ok=True)
    logger.info(f"Created media directory: {media_path}")

app.mount("/media", StaticFiles(directory=media_path), name="media")

@app.get("/")
def root():
    """API info"""
    return {
        "message": settings.PROJECT_NAME,
        "version": "1.0.0",
        "tracked_symbols": settings.TRACKED_SYMBOLS,
        "telegram_channels": settings.TELEGRAM_CHANNELS,
    }

app.include_router(api_router, prefix=settings.API_V1_STR)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)

    try:
        while True:
            data = {}
            
            if bs.binance_stream:
                prices = bs.binance_stream.get_prices()
                if prices:
                    data["prices"] = prices
            if data:
                await websocket.send_json({"type": "update", "data": data})

            await asyncio.sleep(1)

    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}", exc_info=True)
        manager.disconnect(websocket)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)

