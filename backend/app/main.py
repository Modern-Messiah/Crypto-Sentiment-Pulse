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

