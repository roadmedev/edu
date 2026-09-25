from aiogram import BaseMiddleware

from api import users as users_api
from api.client import ApiError


class AuthMiddleware(BaseMiddleware):
    """data['user'] ga foydalanuvchi dict'ini (yoki ro'yxatdan o'tmagan bo'lsa None) qo'yadi."""

    async def __call__(self, handler, event, data):
        tg_user = data.get("event_from_user")
        data["user"] = None

        if tg_user is not None:
            try:
                data["user"] = await users_api.get_by_telegram_id(data["api"], tg_user.id)
            except ApiError:
                # Backend ishlamayapti: foydalanuvchini bilmagan holda davom ettirmaymiz
                bot = data["bot"]
                await bot.send_message(
                    tg_user.id, "Xizmat vaqtincha ishlamayapti, keyinroq urinib ko'ring."
                )
                return None

        return await handler(event, data)