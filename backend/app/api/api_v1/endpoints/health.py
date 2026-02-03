from fastapi import APIRouter
from app.services import binance as bs
from app.core.ws_manager import manager

router = APIRouter()

@router.get("/")
async def health_check():
    connected = (
        bs.binance_stream is not None
        and len(bs.binance_stream.get_prices()) > 0
    )
    return {
        "status": "healthy" if connected else "connecting",
        "binance_connected": connected,
        "active_websocket_clients": len(manager.active_connections),
    }
