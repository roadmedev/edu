from api.client import ApiClient

async def list_courses(api: ApiClient) -> list[dict]:
    return await api.get("/courses")

async def join(api: ApiClient, tg_id: int, course_id: int) -> dict:
    return await api.post("/enrollments", json={"telegramId": tg_id, "courseId": course_id})

async def my_courses(api: ApiClient, tg_id: int) -> list[dict]:
    return await api.get(f"/courses/mine/{tg_id}")


async def check_slot(api: ApiClient, weekday: int, start: str, end: str) -> dict | None:
    res = await api.post("/courses/check-slot",
                         json={"weekday": weekday, "startTime": start, "endTime": end})
    return res["conflict"]


async def create_course(api: ApiClient, tg_id: int, payload: dict) -> dict:
    return await api.post("/courses", json={"telegramId": tg_id, **payload})


async def delete_course(api: ApiClient, tg_id: int, course_id: int) -> dict:
    return await api.delete(f"/courses/{course_id}", params={"telegramId": tg_id})