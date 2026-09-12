from services.api_client import post

async def register_user(full_name: str, phone_number: str, telegram_id: int) -> dict:
    return await post(
        "/register",
        {
            "full_name": full_name,
            "phone_number": phone_number,
            "telegram_id": telegram_id,
        }
    )