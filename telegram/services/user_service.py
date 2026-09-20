# services/user_service.py
from services.api_client import get, post


# ============ KURSLAR ============
async def get_courses_paginated(page: int = 1, limit: int = 10) -> dict:
    return await get(f"/user/courses?page={page}&limit={limit}")


async def get_course_teachers(course_id: int) -> list[dict]:
    result = await get(f"/user/courses/{course_id}/teachers")
    return result.get("teachers", [])


# ============ SO'ROVLAR ============
async def send_course_request(telegram_id: int, course_id: int, message: str = None) -> dict:
    return await post(
        "/user/course-requests",
        {"telegram_id": telegram_id, "course_id": course_id, "message": message}
    )


async def get_my_requests(telegram_id: int) -> list[dict]:
    result = await get(f"/user/my-requests/{telegram_id}")
    return result.get("requests", [])


# ============ MENING KURSLARIM ============
async def get_my_courses(telegram_id: int) -> list[dict]:
    result = await get(f"/user/my-courses/{telegram_id}")
    return result.get("courses", [])


# ============ DARS JADVALI ============
async def get_schedule() -> list[dict]:
    result = await get("/user/schedule")
    return result.get("schedules", [])


# ============ REYTING ============
async def get_my_rating(telegram_id: int) -> dict:
    return await get(f"/user/my-rating/{telegram_id}")


# ============ TAKLIF ============
async def send_suggestion(telegram_id: int, message: str) -> dict:
    return await post("/user/suggestions", {"telegram_id": telegram_id, "message": message})