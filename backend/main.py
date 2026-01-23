import asyncio
import logging
from contextlib import asynccontextmanager
from datetime import datetime, timedelta

# Import module to access global variable dynamically
import binance_stream as bs_module
from database import PriceHistory, SessionLocal, init_db
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import desc

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Отслеживаемые символы
TRACKED_SYMBOLS = [
    "BTCUSDT",
    "ETHUSDT",
    "BNBUSDT",
    "ADAUSDT",
    "SOLUSDT",
    "XRPUSDT",
    "DOGEUSDT",
    "MATICUSDT",
    "DOTUSDT",
    "LINKUSDT",
    "AVAXUSDT",
    "UNIUSDT",
    "LTCUSDT",
    "ARBUSDT",
    "ATOMUSDT",
    "XLMUSDT",
    "TRXUSDT",
    "ETCUSDT",
    "FILUSDT",
    "NEARUSDT",
]


class ConnectionManager:
    """Менеджер WebSocket подключений"""

    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"Client connected. Total: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        logger.info(f"Client disconnected. Total: {len(self.active_connections)}")

    async def broadcast(self, message: dict):
        """Отправка всем подключенным клиентам"""
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                disconnected.append(connection)

        # Удаляем отключившихся
        for conn in disconnected:
            self.disconnect(conn)


manager = ConnectionManager()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle events"""
    # Startup
    init_db()  # Ensure tables exist
    await bs_module.init_binance_stream(TRACKED_SYMBOLS)
    logger.info(f"Backend started. Tracking {len(TRACKED_SYMBOLS)} symbols")

    yield

    # Shutdown
    if bs_module.binance_stream:
        await bs_module.binance_stream.close()
    logger.info("Backend shutdown complete")


app = FastAPI(
    title="Crypto WebSocket API",
    description="Real-time cryptocurrency prices via WebSocket",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS для Vue.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    """API информация"""
    return {
        "message": "Crypto Live Prices API",
        "version": "1.0.0",
        "tracked_symbols": TRACKED_SYMBOLS,
        "endpoints": {
            "websocket": "ws://localhost:8080/ws",
            "rest": "/api/prices",
            "docs": "/docs",
        },
    }


@app.get("/api/prices")
async def get_prices():
    """REST endpoint для текущих цен"""
    if bs_module.binance_stream:
        return {
            "data": bs_module.binance_stream.get_prices(),
            "count": len(bs_module.binance_stream.get_prices()),
        }
    return {"data": {}, "count": 0}


@app.get("/api/history/{symbol}")
async def get_history(symbol: str, period: str = "15m", limit: int = 100):
    """Возвращает историю цен за указанный период (15m, 1h, 24h)"""
    symbol = symbol.upper()

    # Расчет временной метки начала периода
    now = datetime.utcnow()
    if period == "1h":
        start_time = now - timedelta(hours=1)
    elif period == "24h":
        start_time = now - timedelta(days=1)
    elif period == "4h":
        start_time = now - timedelta(hours=4)
    else:  # Default 15m
        start_time = now - timedelta(minutes=15)

    # Сначала проверяем память для очень короткого периода (если лимит позволяет)
    if period == "15m" and bs_module.binance_stream:
        mem_history = bs_module.binance_stream.get_history(symbol)
        if len(mem_history) >= limit:
            return {
                "symbol": symbol,
                "source": "memory",
                "period": period,
                "history": mem_history[-limit:],
            }

    # Берем из БД для любого периода
    db = SessionLocal()
    try:
        query = (
            db.query(PriceHistory)
            .filter(PriceHistory.symbol == symbol, PriceHistory.timestamp >= start_time)
            .order_by(desc(PriceHistory.timestamp))
        )

        # Если период большой (например 24ч), берем больше точек, но лимитируем для графика
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
    except Exception as e:
        logger.error(f"DB Error: {e}")
        return {"symbol": symbol, "source": "error", "history": []}
    finally:
        db.close()


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    connected = (
        bs_module.binance_stream is not None
        and len(bs_module.binance_stream.get_prices()) > 0
    )
    return {
        "status": "healthy" if connected else "connecting",
        "binance_connected": connected,
        "active_websocket_clients": len(manager.active_connections),
    }


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket для real-time обновлений"""
    await manager.connect(websocket)

    try:
        while True:
            if bs_module.binance_stream:
                prices = bs_module.binance_stream.get_prices()
                if prices:
                    await websocket.send_json({"type": "prices", "data": prices})

            await asyncio.sleep(1)  # Отправка каждую секунду

    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)
