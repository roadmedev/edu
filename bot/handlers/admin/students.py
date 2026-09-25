from aiogram import F, Router
from aiogram.exceptions import TelegramAPIError
from aiogram.types import CallbackQuery, Message

from api import admin as admin_api
from api.client import ApiClient, ApiError
from callbacks.admin import StudentAdminCB
from filters.role import RoleFilter
from keyboards.inline.admin import student_detail_kb, student_list_kb
from utils import labels as L
from utils.formatters import format_student_admin_detail, format_students_overview

router = Router(name="admin_students")
router.message.filter(RoleFilter("admin"))
router.callback_query.filter(RoleFilter("admin"))


@router.message(F.text == L.STUDENTS_LIST)
async def list_students(message: Message, api: ApiClient):
    data = await admin_api.students(api, message.from_user.id)
    kb = student_list_kb(data["students"]) if data["students"] else None
    await message.answer(format_students_overview(data["students"]), reply_markup=kb)


@router.callback_query(StudentAdminCB.filter(F.action == "back"))
async def back_to_list(cb: CallbackQuery, api: ApiClient):
    data = await admin_api.students(api, cb.from_user.id)
    kb = student_list_kb(data["students"]) if data["students"] else None
    await cb.message.edit_text(format_students_overview(data["students"]), reply_markup=kb)
    await cb.answer()


@router.callback_query(StudentAdminCB.filter(F.action == "view"))
async def view_student(cb: CallbackQuery, callback_data: StudentAdminCB, api: ApiClient):
    data = await admin_api.students(api, cb.from_user.id)
    s = next((x for x in data["students"] if x["enrollmentId"] == callback_data.enrollment_id), None)
    if not s:
        await cb.answer("Topilmadi", show_alert=True)
        return
    await cb.message.edit_text(
        format_student_admin_detail(s),
        reply_markup=student_detail_kb(callback_data.enrollment_id, s["status"] == "paid"),
    )
    await cb.answer()


@router.callback_query(StudentAdminCB.filter(F.action == "paid"))
async def mark_paid(cb: CallbackQuery, callback_data: StudentAdminCB, api: ApiClient):
    try:
        await admin_api.mark_student_paid(api, cb.from_user.id, callback_data.enrollment_id)
    except ApiError as e:
        await cb.answer(e.message, show_alert=True)
        return
    data = await admin_api.students(api, cb.from_user.id)
    s = next((x for x in data["students"] if x["enrollmentId"] == callback_data.enrollment_id), None)
    await cb.message.edit_text(format_student_admin_detail(s), reply_markup=student_detail_kb(callback_data.enrollment_id, True))
    await cb.answer("✅ Qayd etildi")


@router.callback_query(StudentAdminCB.filter(F.action == "remind"))
async def send_reminder(cb: CallbackQuery, callback_data: StudentAdminCB, api: ApiClient):
    data = await admin_api.students(api, cb.from_user.id)
    s = next((x for x in data["students"] if x["enrollmentId"] == callback_data.enrollment_id), None)
    if not s:
        await cb.answer("Topilmadi", show_alert=True)
        return
    try:
        await cb.bot.send_message(
            s["studentTgId"],
            f"⏰ Eslatma: «{s['courseTitle']}» kursi bo'yicha oylik to'lovingizni amalga oshirishingizni so'raymiz.",
        )
        await cb.answer("📨 So'rov yuborildi", show_alert=True)
    except TelegramAPIError:
        await cb.answer("Foydalanuvchiga xabar yuborib bo'lmadi.", show_alert=True)