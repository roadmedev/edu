from aiogram import F, Router
from aiogram.types import Message

from api import enrollments as enr_api
from api.client import ApiClient
from filters.role import RoleFilter
from utils import labels as L
from utils.formatters import format_my_courses

router = Router(name="student_my")
router.message.filter(RoleFilter("student"))


@router.message(F.text == L.MY)
async def my_courses(message: Message, api: ApiClient):
    items = await enr_api.my_courses(api, message.from_user.id)
    await message.answer(format_my_courses(items))