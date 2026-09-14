from services.api_client import get


async def get_subjects() -> list[dict]:
    result = await get("/admin/subjects")
    return result.get("subjects", [])


async def get_groups_by_subject(subject_id: int) -> list[dict]:
    result = await get(f"/admin/subjects/{subject_id}/groups")
    return result.get("groups", [])


async def get_students_by_group(group_id: int) -> list[dict]:
    result = await get(f"/admin/groups/{group_id}/students")
    return result.get("students", [])


async def get_student_detail(student_id: int) -> dict:
    return await get(f"/admin/students/{student_id}")