import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from app.api.api_v1.api import api_router
from app.core.config import settings
from app.core.ws_manager import manager
from app.services import binance as bs
from app.db.session import engine
from app.db.base import Base

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):

    Base.metadata.create_all(bind=engine)
    
    await bs.init_binance_stream(settings.TRACKED_SYMBOLS)
    logger.info(f"Backend started. Tracking {len(settings.TRACKED_SYMBOLS)} symbols")

    yield

    if bs.binance_stream:
        await bs.binance_stream.close()
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

@app.get("/")
def root():
    """API info"""
    return {
        "message": settings.PROJECT_NAME,
        "version": "1.0.0",
        "tracked_symbols": settings.TRACKED_SYMBOLS,
    }

app.include_router(api_router, prefix=settings.API_V1_STR)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)

    try:
        while True:
            if bs.binance_stream:
                prices = bs.binance_stream.get_prices()
                if prices:
                    await websocket.send_json({"type": "prices", "data": prices})

            await asyncio.sleep(1)

    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}", exc_info=True)
        manager.disconnect(websocket)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
