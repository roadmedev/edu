from api.client import ApiClient


async def get_balance(api: ApiClient, tg_id: int) -> dict:
    return await api.get(f"/teachers/{tg_id}/balance")