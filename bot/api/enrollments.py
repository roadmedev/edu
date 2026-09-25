from api.client import ApiClient


async def decide(api: ApiClient, tg_id: int, enrollment_id: int, action: str) -> dict:
    return await api.post(f"/enrollments/{enrollment_id}/decision",
                          json={"telegramId": tg_id, "action": action})


async def accept_terms(api: ApiClient, tg_id: int, enrollment_id: int) -> dict:
    return await api.post(f"/enrollments/{enrollment_id}/accept-terms", json={"telegramId": tg_id})

async def my_courses(api: ApiClient, tg_id: int) -> list[dict]:
    return await api.get(f"/enrollments/mine/{tg_id}")


async def course_rating(api: ApiClient, tg_id: int, course_id: int) -> list[dict]:
    return await api.get(f"/enrollments/course/{course_id}/rating", params={"telegramId": tg_id})