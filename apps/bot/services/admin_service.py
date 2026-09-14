from services.api_client import get

async def get_center_stats() -> dict:
    return await get("/admin/stats")