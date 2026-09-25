from api.client import ApiClient


async def course_students(api: ApiClient, tg_id: int, course_id: int) -> dict:
    return await api.get(f"/courses/{course_id}/students", params={"telegramId": tg_id})

async def save_attendance(api: ApiClient, tg_id: int, course_id: int, records: list[dict]) -> dict:
    return await api.post(f"/courses/{course_id}/attendance", json={"telegramId": tg_id, "records": records})

