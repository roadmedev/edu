from api.client import ApiClient, ApiError


async def get_by_telegram_id(api: ApiClient, tg_id: int) -> dict | None:
    try:
        return await api.get(f"/users/by-telegram/{tg_id}")
    except ApiError as e:
        if e.status == 404:
            return None
        raise


async def register(api: ApiClient, tg_id: int, full_name: str, phone: str) -> dict:
    return await api.post(
        "/users",
        json={"telegramId": tg_id, "fullName": full_name, "phone": phone},
    )