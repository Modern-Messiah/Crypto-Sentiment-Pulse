from fastapi import APIRouter
from app.services.fear_greed import get_fear_greed_index

router = APIRouter()

@router.get("/fear-greed")
async def read_fear_greed():
    """
    Get the latest Fear & Greed Index.
    """
    data = await get_fear_greed_index()
    if not data:
        # Return fallback/default if API fails
        return {
            "value": 50,
            "value_classification": "Neutral",
            "timestamp": None,
            "error": "Failed to fetch data"
        }
    return data
