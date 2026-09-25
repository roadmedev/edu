from aiogram import F, Router
from aiogram.types import Message

from api import suggestions as suggestions_api
from api.client import ApiClient, ApiError
from filters.role import RoleFilter
from utils import labels as L
from utils.formatters import format_suggestions

router = Router(name="admin_suggestions")
router.message.filter(RoleFilter("admin"))


@router.message(F.text == L.SUGGESTION_BOX)
async def show_suggestions(message: Message, api: ApiClient):
    try:
        rows = await suggestions_api.list_suggestions(api, message.from_user.id)
    except ApiError as e:
        await message.answer(f"⚠️ Xatolik: {e.message}")
        return
    await message.answer(format_suggestions(rows))