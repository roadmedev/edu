from api.client import ApiClient


async def stats(api: ApiClient, tg_id: int) -> dict:
    return await api.get(f"/admin/{tg_id}/stats")


async def plain_users(api: ApiClient, tg_id: int) -> list[dict]:
    return await api.get(f"/admin/{tg_id}/users")


async def teachers(api: ApiClient, tg_id: int) -> list[dict]:
    return await api.get(f"/admin/{tg_id}/teachers")


async def teacher_courses(api: ApiClient, tg_id: int, teacher_id: int) -> list[dict]:
    return await api.get(f"/admin/{tg_id}/teachers/{teacher_id}/courses")


async def teacher_candidates(api: ApiClient, tg_id: int) -> list[dict]:
    return await api.get(f"/admin/{tg_id}/teacher-candidates")


async def add_teacher(api: ApiClient, tg_id: int, payload: dict) -> dict:
    return await api.post(f"/admin/{tg_id}/teachers", json=payload)


async def delete_teacher(api: ApiClient, tg_id: int, teacher_id: int) -> dict:
    return await api.delete(f"/admin/{tg_id}/teachers/{teacher_id}")


async def students(api: ApiClient, tg_id: int) -> dict:
    return await api.get(f"/admin/{tg_id}/students")


async def mark_student_paid(api: ApiClient, tg_id: int, enrollment_id: int) -> dict:
    return await api.post(f"/admin/{tg_id}/students/{enrollment_id}/mark-paid")