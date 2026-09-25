from api.client import ApiClient


async def mark_paid(api: ApiClient, tg_id: int, enrollment_id: int) -> dict:
    return await api.post(f"/payments/{enrollment_id}/mark-paid", json={"telegramId": tg_id})


async def mark_partial(api: ApiClient, tg_id: int, enrollment_id: int, amount: int) -> dict:
    return await api.post(f"/payments/{enrollment_id}/mark-partial", json={"telegramId": tg_id, "amount": amount})
