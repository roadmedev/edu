from aiogram import F, Router
from aiogram.types import CallbackQuery, Message

from api import courses as courses_api
from api.client import ApiClient, ApiError
from callbacks.courses import JoinCB
from filters.role import RoleFilter
from keyboards.inline.courses import join_keyboard
from utils import labels as L
from utils.formatters import format_course

from aiogram.exceptions import TelegramAPIError

from keyboards.inline.enrollments import request_kb
from utils.texts import teacher_request

router = Router(name="user_courses")
# user ham, student ham yangi kurslarni ko'ra oladi
router.message.filter(RoleFilter("user", "student"))
router.callback_query.filter(RoleFilter("user", "student"))


@router.message(F.text == L.COURSES)
async def show_courses(message: Message, api: ApiClient):
    courses = await courses_api.list_courses(api)
    if not courses:
        await message.answer("Hozircha kurslar mavjud emas.")
        return

    for c in courses:
        text = format_course(c)
        kb = join_keyboard(c["id"])
        photo = c.get("photo") or c.get("teacherPhoto")
        if photo:
            await message.answer_photo(photo, caption=text, reply_markup=kb)
        else:
            await message.answer(text, reply_markup=kb)


@router.callback_query(JoinCB.filter())
async def join_course(cb: CallbackQuery, callback_data: JoinCB, api: ApiClient):
    try:
        enr = await courses_api.join(api, cb.from_user.id, callback_data.course_id)
    except ApiError as e:
        text = e.message if 400 <= e.status < 500 else "Xatolik yuz berdi, keyinroq urinib ko'ring."
        await cb.answer(text, show_alert=True)
        return

    try:
        await cb.bot.send_message(enr["teacherTgId"], teacher_request(enr), reply_markup=request_kb(enr["id"]))
    except TelegramAPIError:
        # O'qituvchi botni bloklagan yoki hech qachon /start bosmagan bo'lishi mumkin
        await cb.answer("So'rov saqlandi, lekin o'qituvchiga xabar yetkazib bo'lmadi. Administrator bilan bog'laning.",
                        show_alert=True)
        return

    await cb.answer("✅ So'rovingiz o'qituvchiga yuborildi. Javobni kuting.", show_alert=True)