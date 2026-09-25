from aiogram import F, Router
from aiogram.types import Message

from api import admin as admin_api
from api.client import ApiClient
from filters.role import RoleFilter
from utils import labels as L
from utils.formatters import format_stats

router = Router(name="admin_stats")
router.message.filter(RoleFilter("admin"))


@router.message(F.text == L.STATS)
async def show_stats(message: Message, api: ApiClient):
    data = await admin_api.stats(api, message.from_user.id)
    await message.answer(format_stats(data))