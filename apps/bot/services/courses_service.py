from services.api_client import get

async def get_courses() -> list[dict]:
    result = await get("/courses")
    return result.get("courses", [])