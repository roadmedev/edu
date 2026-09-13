from services.api_client import post, get

async def register_user(full_name: str, phone_number: str, telegram_id: int) -> dict:
    return await post(
        "/register",
        {
            "full_name": full_name,
            "phone_number": phone_number,
            "telegram_id": telegram_id,
        }
    )

async def get_user_by_telegram_id(telegram_id: int) -> dict:
    return await get(f"/users/by-telegram/{telegram_id}")