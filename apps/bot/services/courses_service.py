from services.api_client import get, post


async def get_courses() -> list[dict]:
    result = await get("/courses")
    return result.get("courses", [])


async def get_course_detail(course_id: int) -> dict:
    return await get(f"/courses/{course_id}")


async def enroll_in_course(telegram_id: int, course_id: int) -> dict:
    return await post("/enroll", {"telegram_id": telegram_id, "course_id": course_id})