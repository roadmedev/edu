# services/teacher_service.py
from services.api_client import get, post, put


# ============ PROFIL ============
async def get_teacher_profile(telegram_id: int) -> dict:
    return await get(f"/teacher/profile/{telegram_id}")


async def update_teacher_profile(telegram_id: int, field: str, value) -> dict:
    return await put(f"/teacher/profile/{telegram_id}", {"field": field, "value": value})


# ============ KURSLAR ============
async def get_my_courses(telegram_id: int) -> list[dict]:
    result = await get(f"/teacher/courses/{telegram_id}")
    return result.get("courses", [])


async def create_course(data: dict) -> dict:
    return await post("/teacher/courses", data)


# ============ DARS JADVALI ============
async def add_schedule(data: dict) -> dict:
    return await post("/teacher/schedules", data)


async def get_course_schedules(course_id: int) -> list[dict]:
    result = await get(f"/teacher/schedules/{course_id}")
    return result.get("schedules", [])


# ============ SO'ROVLAR ============
async def get_teacher_requests(telegram_id: int) -> list[dict]:
    result = await get(f"/teacher/requests/{telegram_id}")
    return result.get("requests", [])


async def respond_to_request(
    request_id: int,
    status: str,
    rejection_reason: str = None,
) -> dict:
    return await put(
        f"/teacher/requests/{request_id}",
        {"status": status, "rejection_reason": rejection_reason},
    )


# ============ O'QUVCHILAR ============
async def get_teacher_students(telegram_id: int) -> list[dict]:
    result = await get(f"/teacher/students/{telegram_id}")
    return result.get("students", [])


async def mark_payment(
    telegram_id: int,
    student_id: int,
    course_id: int,
    amount: float,
) -> dict:
    return await post(
        f"/teacher/students/{telegram_id}/payment",
        {"student_id": student_id, "course_id": course_id, "amount": amount},
    )


async def set_grade(data: dict) -> dict:
    return await post("/teacher/grades", data)


# ============ BALANS ============
async def get_balance(telegram_id: int) -> dict:
    return await get(f"/teacher/balance/{telegram_id}")


# ============ TAKLIF ============
async def send_suggestion(telegram_id: int, message: str) -> dict:
    return await post("/user/suggestions", {"telegram_id": telegram_id, "message": message})