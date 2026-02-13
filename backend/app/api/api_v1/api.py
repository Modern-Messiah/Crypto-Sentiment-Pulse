from fastapi import APIRouter
from app.api.api_v1.endpoints import prices, history, health, channels, messages, cryptopanic_news, sentiment

api_router = APIRouter()
api_router.include_router(prices.router, prefix="/prices", tags=["prices"])
api_router.include_router(history.router, prefix="/history", tags=["history"])
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(channels.router, prefix="/channels", tags=["telegram"])
api_router.include_router(messages.router, prefix="/messages", tags=["telegram"])
api_router.include_router(cryptopanic_news.router, prefix="/news", tags=["news"])
api_router.include_router(sentiment.router, prefix="/sentiment", tags=["sentiment"])
