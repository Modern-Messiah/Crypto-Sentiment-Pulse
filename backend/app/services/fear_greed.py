import httpx
import logging

logger = logging.getLogger(__name__)

FEAR_GREED_API_URL = "https://api.alternative.me/fng/"

async def get_fear_greed_index():
    """
    Fetch the latest Fear & Greed Index from alternative.me
    """
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                FEAR_GREED_API_URL,
                params={"limit": 1, "format": "json"}
            )
            response.raise_for_status()
            data = response.json()
            
            # The API returns data in 'data' list
            # Structure: {"name": "Fear and Greed Index", "data": [{"value": "25", "value_classification": "Extreme Fear", "timestamp": "..."}]}
            if data and "data" in data and len(data["data"]) > 0:
                item = data["data"][0]
                return {
                    "value": int(item["value"]),
                    "value_classification": item["value_classification"],
                    "timestamp": item["timestamp"],
                    "time_until_update": data.get("metadata", {}).get("time_until_update")
                }
            return None
            
    except Exception as e:
        logger.error(f"Error fetching Fear & Greed Index: {e}")
        return None
