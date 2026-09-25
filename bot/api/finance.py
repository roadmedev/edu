from api.client import ApiClient


async def get_finance(api: ApiClient, tg_id: int) -> dict:
    return await api.get(f"/admin/{tg_id}/finance")


async def mark_payout_paid(api: ApiClient, tg_id: int, teacher_id: int) -> dict:
    return await api.post(f"/admin/{tg_id}/payouts/{teacher_id}/mark-paid")


async def mark_payout_partial(api: ApiClient, tg_id: int, teacher_id: int, amount: int) -> dict:
    return await api.post(f"/admin/{tg_id}/payouts/{teacher_id}/mark-partial", json={"amount": amount})