from services.api_client import get, post


async def get_paid_students() -> list[dict]:
    result = await get("/admin/payments/paid")
    return result.get("students", [])


async def get_debtors() -> list[dict]:
    result = await get("/admin/payments/debtors")
    return result.get("students", [])


async def mark_paid(enrollment_id: int) -> dict:
    return await post("/admin/payments/mark-paid", {"enrollment_id": enrollment_id})