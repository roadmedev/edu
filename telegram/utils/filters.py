# utils/filters.py
from aiogram.filters import BaseFilter
from aiogram.types import Message, CallbackQuery

from services.auth_service import get_user_by_telegram_id


class IsAdmin(BaseFilter):
    async def __call__(self, event: Message | CallbackQuery) -> bool:
        user_id = event.from_user.id
        result = await get_user_by_telegram_id(user_id)
        user = result.get("user")
        return user is not None and user.get("role") == "admin"


class IsTeacher(BaseFilter):
    async def __call__(self, event: Message | CallbackQuery) -> bool:
        user_id = event.from_user.id
        result = await get_user_by_telegram_id(user_id)
        user = result.get("user")
        return user is not None and user.get("role") == "teacher"


class IsUser(BaseFilter):
    async def __call__(self, event: Message | CallbackQuery) -> bool:
        user_id = event.from_user.id
        result = await get_user_by_telegram_id(user_id)
        user = result.get("user")
        return user is not None and user.get("role") == "user"