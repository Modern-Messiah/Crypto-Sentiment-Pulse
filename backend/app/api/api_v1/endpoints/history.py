from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import desc, text
from datetime import datetime, timedelta
from app.db.session import get_db
from app.models.price_history import PriceHistory
from app.services import binance as bs

router = APIRouter()

@router.get("/{symbol}")
@router.get("/{symbol}/")
async def get_history(symbol: str, period: str = "15m", limit: int = 1000, db: Session = Depends(get_db)):
    symbol = symbol.upper().rstrip("/")

    now = datetime.utcnow()
    if period == "1m":
        start_time = now - timedelta(seconds=90)
    elif period == "5m":
        start_time = now - timedelta(minutes=5)
    elif period == "1h":
        start_time = now - timedelta(hours=1)
    elif period == "4h":
        start_time = now - timedelta(hours=4)
    elif period == "24h":
        start_time = now - timedelta(days=1)
    else:
        start_time = now - timedelta(minutes=15)


    # Use bucketing based on period to avoid returning thousands of points
    # 1m, 5m, 15m -> no bucketing (1-10s resolution)
    # 1h -> 1m buckets
    # 4h -> 5m buckets
    # 24h -> 15m buckets
    
    bucket_interval = None
    if period == "1h":
        bucket_interval = "1 minute"
    elif period == "4h":
        bucket_interval = "5 minutes"
    elif period == "24h":
        bucket_interval = "15 minutes"

    if bucket_interval:
        # Use raw SQL for efficient time bucketing in PostgreSQL
        sql = f"""
            SELECT 
                date_trunc('minute', timestamp) - (CAST(extract(minute FROM timestamp) AS integer) % {bucket_interval.split()[0]}) * interval '1 minute' as bucket,
                AVG(price) as avg_price
            FROM price_history
            WHERE symbol = :symbol AND timestamp >= :start_time
            GROUP BY bucket
            ORDER BY bucket DESC
            LIMIT :limit
        """
        # Note: The above is a bit complex for generic grouping. 
        # Simpler approach: floor the timestamp to interval
        
        if period == "1h":
            # 1 minute buckets
            sql = """
                SELECT date_trunc('minute', timestamp) as bucket, AVG(price) as avg_price
                FROM price_history
                WHERE symbol = :symbol AND timestamp >= :start_time
                GROUP BY bucket ORDER BY bucket DESC LIMIT :limit
            """
        elif period == "4h":
            # 5 minute buckets
            sql = """
                SELECT 
                    to_timestamp(floor(extract(epoch from timestamp) / 300) * 300) as bucket,
                    AVG(price) as avg_price
                FROM price_history
                WHERE symbol = :symbol AND timestamp >= :start_time
                GROUP BY bucket ORDER BY bucket DESC LIMIT :limit
            """
        else: # 24h
            # 15 minute buckets
            sql = """
                SELECT 
                    to_timestamp(floor(extract(epoch from timestamp) / 900) * 900) as bucket,
                    AVG(price) as avg_price
                FROM price_history
                WHERE symbol = :symbol AND timestamp >= :start_time
                GROUP BY bucket ORDER BY bucket DESC LIMIT :limit
            """
            
        result = db.execute(
            text(sql), 
            {"symbol": symbol, "start_time": start_time, "limit": limit}
        ).fetchall()
        
        formatted_history = [
            {"time": r[0].timestamp() * 1000, "price": float(r[1])}
            for r in reversed(result)
        ]
    else:
        # Standard query for 15m or small datasets
        query = (
            db.query(PriceHistory)
            .filter(PriceHistory.symbol == symbol, PriceHistory.timestamp >= start_time)
            .order_by(desc(PriceHistory.timestamp))
            .limit(limit)
        )
        db_history = query.all()
        formatted_history = [
            {"time": h.timestamp.timestamp() * 1000, "price": h.price}
            for h in reversed(db_history)
        ]

    return {
        "symbol": symbol,
        "source": "database",
        "period": period,
        "count": len(formatted_history),
        "history": formatted_history,
    }
