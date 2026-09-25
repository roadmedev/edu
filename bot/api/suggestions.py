from api.client import ApiClient


async def send_suggestion(api: ApiClient, tg_id: int, text: str) -> dict:
    return await api.post("/suggestions", json={"telegramId": tg_id, "text": text})


async def list_suggestions(api: ApiClient, tg_id: int) -> list[dict]:
    return await api.get(f"/admin/{tg_id}/suggestions")