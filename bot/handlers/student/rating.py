from aiogram import F, Router
from aiogram.types import CallbackQuery, Message

from api import enrollments as enr_api
from api.client import ApiClient
from callbacks.rating import RatingCB
from filters.role import RoleFilter
from keyboards.inline.rating import course_pick_kb
from utils import labels as L
from utils.formatters import format_rating

router = Router(name="student_rating")
router.message.filter(RoleFilter("student"))
router.callback_query.filter(RoleFilter("student"))


@router.message(F.text == L.RATING)
async def rating_entry(message: Message, api: ApiClient):
    items = await enr_api.my_courses(api, message.from_user.id)
    if not items:
        await message.answer("Reytingni ko'rish uchun avval biror faol kursingiz bo'lishi kerak.")
        return
    if len(items) == 1:
        rows = await enr_api.course_rating(api, message.from_user.id, items[0]["courseId"])
        await message.answer(format_rating(rows))
        return
    await message.answer("Qaysi kurs bo'yicha reytingni ko'rmoqchisiz?", reply_markup=course_pick_kb(items))


@router.callback_query(RatingCB.filter())
async def rating_pick(cb: CallbackQuery, callback_data: RatingCB, api: ApiClient):
    rows = await enr_api.course_rating(api, cb.from_user.id, callback_data.course_id)
    await cb.message.edit_text(format_rating(rows))
    await cb.answer()