from html import escape

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from api import courses as courses_api
from api.client import ApiClient, ApiError
from callbacks.teacher import MyCourseCB
from filters.role import RoleFilter
from keyboards.inline.teacher import confirm_delete_kb, my_course_kb
from keyboards.reply.menu import main_menu
from keyboards.reply.teacher import teacher_my_menu
from utils import labels as L
from utils.cards import send_course_card
from utils.formatters import format_timetable

router = Router(name="teacher_my_courses")
router.message.filter(RoleFilter("teacher"))
router.callback_query.filter(RoleFilter("teacher"))


async def _find_course(api: ApiClient, tg_id: int, course_id: int) -> dict | None:
    return next((c for c in await courses_api.my_courses(api, tg_id) if c["id"] == course_id), None)


# ---------- Reply menyu tugmalari (yarim qolgan FSM'ni ham tozalaydi) ----------
@router.message(F.text == L.MY)
async def my_section(message: Message, state: FSMContext, api: ApiClient):
    await state.clear()
    courses = await courses_api.my_courses(api, message.from_user.id)
    head = ("📚 <b>Mening kurslarim:</b>" if courses
            else "Sizda hali kurs yo'q. «➕ Yangi kurs qo'shish» tugmasini bosing.")
    await message.answer(head, reply_markup=teacher_my_menu())  # menyu shu yerda almashadi

    for c in courses:
        await send_course_card(message, c, my_course_kb(c["id"], bool(c.get("certificate"))))


@router.message(F.text == L.BACK)
async def back_to_main(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Asosiy menyu", reply_markup=main_menu("teacher"))


@router.message(F.text == L.SCHEDULE)
async def show_timetable(message: Message, state: FSMContext, api: ApiClient):
    await state.clear()
    await message.answer(format_timetable(await courses_api.list_courses(api)))


# ---------- Kurs kartochkasidagi tugmalar ----------
@router.callback_query(MyCourseCB.filter(F.action == "cert"))
async def show_certificate(cb: CallbackQuery, callback_data: MyCourseCB, api: ApiClient):
    course = await _find_course(api, cb.from_user.id, callback_data.course_id)
    if not course or not course.get("certificate"):
        await cb.answer("Sertifikat topilmadi", show_alert=True)
        return
    await cb.message.answer_photo(course["certificate"], caption=f"📜 «{escape(course['title'])}» sertifikati")
    await cb.answer()


@router.callback_query(MyCourseCB.filter(F.action == "del"))
async def ask_delete(cb: CallbackQuery, callback_data: MyCourseCB):
    await cb.message.edit_reply_markup(reply_markup=confirm_delete_kb(callback_data.course_id))
    await cb.answer("Kurs o'chirilsinmi?")


@router.callback_query(MyCourseCB.filter(F.action == "delno"))
async def cancel_delete(cb: CallbackQuery, callback_data: MyCourseCB, api: ApiClient):
    course = await _find_course(api, cb.from_user.id, callback_data.course_id)
    has_cert = bool(course and course.get("certificate"))
    await cb.message.edit_reply_markup(reply_markup=my_course_kb(callback_data.course_id, has_cert))
    await cb.answer()


@router.callback_query(MyCourseCB.filter(F.action == "delyes"))
async def do_delete(cb: CallbackQuery, callback_data: MyCourseCB, api: ApiClient):
    try:
        await courses_api.delete_course(api, cb.from_user.id, callback_data.course_id)
    except ApiError as e:
        text = e.message if 400 <= e.status < 500 else "Xatolik yuz berdi, keyinroq urinib ko'ring."
        await cb.answer(text, show_alert=True)
        return
    await cb.message.delete()
    await cb.message.answer("🗑 Kurs o'chirildi.")
    await cb.answer()