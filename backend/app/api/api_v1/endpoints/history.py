from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import desc
from datetime import datetime, timedelta
from app.db.session import get_db
from app.models.price_history import PriceHistory
from app.services import binance as bs

router = APIRouter()

@router.get("/{symbol}")
@router.get("/{symbol}/")
async def get_history(symbol: str, period: str = "15m", limit: int = 100, db: Session = Depends(get_db)):
    symbol = symbol.upper().rstrip("/")

    now = datetime.utcnow()
    if period == "1h":
        start_time = now - timedelta(hours=1)
    elif period == "24h":
        start_time = now - timedelta(days=1)
    elif period == "4h":
        start_time = now - timedelta(hours=4)
    else:
        start_time = now - timedelta(minutes=15)

    if period == "15m" and bs.binance_stream:
        mem_history = bs.binance_stream.get_history(symbol)
        if mem_history:
            return {
                "symbol": symbol,
                "source": "memory",
                "period": period,
                "history": mem_history[-limit:],
            }

    query = (
        db.query(PriceHistory)
        .filter(PriceHistory.symbol == symbol, PriceHistory.timestamp >= start_time)
        .order_by(desc(PriceHistory.timestamp))
    )

    db_history = query.limit(limit * 2 if period == "24h" else limit).all()

    formatted_history = [
        {"time": h.timestamp.timestamp() * 1000, "price": h.price}
        for h in reversed(db_history)
    ]
    return {
        "symbol": symbol,
        "source": "database",
        "period": period,
        "history": formatted_history,
    }
