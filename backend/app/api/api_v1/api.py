from fastapi import APIRouter
from app.api.api_v1.endpoints import prices, history, health

api_router = APIRouter()
api_router.include_router(prices.router, prefix="/prices", tags=["prices"])
api_router.include_router(history.router, prefix="/history", tags=["history"])
api_router.include_router(health.router, prefix="/health", tags=["health"])
