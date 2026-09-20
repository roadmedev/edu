# services/admin_service.py
from services.api_client import get, put


# ============ STATISTIKA ============
async def get_center_stats() -> dict:
    return await get("/admin/stats")


# ============ MOLIYA ============
async def get_finance_summary() -> dict:
    return await get("/admin/finance")


async def get_finance_history(history_type: str) -> dict:
    return await get(f"/admin/finance/history?type={history_type}")


async def get_finance_shares() -> dict:
    return await get("/admin/finance/shares")


# ============ O'QITUVCHILAR ============
async def get_teachers() -> list[dict]:
    result = await get("/admin/teachers")
    return result.get("teachers", [])


async def get_teacher_detail(teacher_id: int) -> dict:
    return await get(f"/admin/teachers/{teacher_id}")


async def create_teacher(data: dict) -> dict:
    from services.api_client import post
    return await post("/admin/teachers", data)


async def update_teacher_field(teacher_id: int, field: str, value) -> dict:
    return await put(f"/admin/teachers/{teacher_id}", {"field": field, "value": value})


async def delete_teacher(teacher_id: int) -> dict:
    from services.api_client import delete
    return await delete(f"/admin/teachers/{teacher_id}")


# ============ O'QUVCHILAR ============
async def get_students(role: str | None = None) -> list[dict]:
    endpoint = "/admin/users"
    if role:
        endpoint += f"?role={role}"
    result = await get(endpoint)
    return result.get("users", [])


async def get_student_detail(student_id: int) -> dict:
    return await get(f"/admin/students/{student_id}")


# ============ FANLAR / GURUHLAR ============
async def get_subjects() -> list[dict]:
    result = await get("/admin/subjects")
    return result.get("subjects", [])


async def get_groups_by_subject(subject_id: int) -> list[dict]:
    result = await get(f"/admin/subjects/{subject_id}/groups")
    return result.get("groups", [])


async def get_students_by_group(group_id: int) -> list[dict]:
    result = await get(f"/admin/groups/{group_id}/students")
    return result.get("students", [])


# ============ TO'LOVLAR ============
async def get_paid_students() -> list[dict]:
    result = await get("/admin/payments/paid")
    return result.get("students", [])


async def get_debtors() -> list[dict]:
    result = await get("/admin/payments/debtors")
    return result.get("students", [])


# ============ TAKLIF QUTISI ============
async def get_suggestions(status: str = "new") -> list[dict]:
    result = await get(f"/admin/suggestions?status={status}")
    return result.get("suggestions", [])


async def mark_suggestion(suggestion_id: int, status: str) -> dict:
    return await put(f"/admin/suggestions/{suggestion_id}", {"status": status})