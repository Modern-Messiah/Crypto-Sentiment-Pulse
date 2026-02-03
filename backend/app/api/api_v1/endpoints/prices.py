from fastapi import APIRouter
from app.services import binance as bs

router = APIRouter()

@router.get("/")
async def get_prices():
    if bs.binance_stream:
        return {
            "data": bs.binance_stream.get_prices(),
            "count": len(bs.binance_stream.get_prices()),
        }
    return {"data": {}, "count": 0}
