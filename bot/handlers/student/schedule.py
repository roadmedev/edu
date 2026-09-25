from aiogram import F, Router
from aiogram.types import Message

from api import courses as courses_api
from api.client import ApiClient
from filters.role import RoleFilter
from utils import labels as L
from utils.formatters import format_timetable

router = Router(name="student_schedule")
router.message.filter(RoleFilter("student"))


@router.message(F.text == L.SCHEDULE)
async def schedule(message: Message, api: ApiClient):
    await message.answer(format_timetable(await courses_api.list_courses(api)))