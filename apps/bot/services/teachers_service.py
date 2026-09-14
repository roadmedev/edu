from services.api_client import get, post, put, delete


async def get_teachers() -> list[dict]:
    result = await get("/admin/teachers")
    return result.get("teachers", [])


async def get_teacher_detail(teacher_id: int) -> dict:
    return await get(f"/admin/teachers/{teacher_id}")


async def create_teacher(data: dict) -> dict:
    return await post("/admin/teachers", data)


async def update_teacher_field(teacher_id: int, field: str, value) -> dict:
    return await put(f"/admin/teachers/{teacher_id}", {"field": field, "value": value})


async def delete_teacher(teacher_id: int) -> dict:
    return await delete(f"/admin/teachers/{teacher_id}")