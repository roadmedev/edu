from html import escape

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from api import admin as admin_api
from api.client import ApiClient, ApiError
from callbacks.admin import CandidateCB, TeacherAdminCB, TeacherFlowCB
from filters.role import RoleFilter
from keyboards.inline.admin import (
    add_teacher_kb, candidates_kb, confirm_delete_teacher_kb, skip_cert_kb, teacher_card_kb,
)
from states.teacher_add import TeacherAdd
from utils import labels as L
from utils.cards import send_course_card
from utils.formatters import format_teacher_card

router = Router(name="admin_teachers")
router.message.filter(RoleFilter("admin"))
router.callback_query.filter(RoleFilter("admin"))


@router.message(F.text == L.TEACHERS)
async def list_teachers(message: Message, api: ApiClient):
    teachers = await admin_api.teachers(api, message.from_user.id)
    await message.answer(
        "👨‍🏫 <b>O'qituvchilar</b>" if teachers else "Hozircha o'qituvchi yo'q.",
        reply_markup=add_teacher_kb(),
    )
    for t in teachers:
        text, kb = format_teacher_card(t), teacher_card_kb(t["id"])
        if t.get("photo"):
            await message.answer_photo(t["photo"], caption=text, reply_markup=kb)
        else:
            await message.answer(text, reply_markup=kb)


@router.callback_query(TeacherAdminCB.filter(F.action == "view"))
async def view_teacher_courses(cb: CallbackQuery, callback_data: TeacherAdminCB, api: ApiClient):
    courses = await admin_api.teacher_courses(api, cb.from_user.id, callback_data.teacher_id)
    if not courses:
        await cb.message.answer("Bu o'qituvchining hozircha kursi yo'q.")
    for c in courses:
        await send_course_card(cb.message, c)
    await cb.answer()


@router.callback_query(TeacherAdminCB.filter(F.action == "del"))
async def ask_delete_teacher(cb: CallbackQuery, callback_data: TeacherAdminCB):
    await cb.message.answer(
        "❗️ Ushbu o'qituvchini o'chirsangiz, uning barcha kurslari yopiladi. Davom etamizmi?",
        reply_markup=confirm_delete_teacher_kb(callback_data.teacher_id),
    )
    await cb.answer()


@router.callback_query(TeacherAdminCB.filter(F.action == "delno"))
async def cancel_delete_teacher(cb: CallbackQuery):
    await cb.message.edit_reply_markup(reply_markup=None)
    await cb.answer("Bekor qilindi")


@router.callback_query(TeacherAdminCB.filter(F.action == "delyes"))
async def do_delete_teacher(cb: CallbackQuery, callback_data: TeacherAdminCB, api: ApiClient):
    try:
        result = await admin_api.delete_teacher(api, cb.from_user.id, callback_data.teacher_id)
    except ApiError as e:
        await cb.answer(e.message, show_alert=True)
        return
    await cb.message.edit_text(f"🗑 <b>{escape(result['fullName'])}</b> o'qituvchilar safidan chiqarildi.")
    await cb.answer()


# ---------- Yangi o'qituvchi qo'shish ----------
@router.callback_query(F.data == "admin_add_teacher")
async def start_add_teacher(cb: CallbackQuery, api: ApiClient):
    candidates = await admin_api.teacher_candidates(api, cb.from_user.id)
    if not candidates:
        await cb.answer("Hozircha nomzod (oddiy foydalanuvchi) yo'q.", show_alert=True)
        return
    await cb.message.answer("Qaysi foydalanuvchini o'qituvchi qilmoqchisiz?", reply_markup=candidates_kb(candidates))
    await cb.answer()


@router.callback_query(CandidateCB.filter())
async def pick_candidate(cb: CallbackQuery, callback_data: CandidateCB, state: FSMContext):
    await state.set_state(TeacherAdd.photo)
    await state.update_data(user_id=callback_data.user_id)
    await cb.message.edit_text("1/3. O'qituvchining <b>rasmini</b> yuboring:")
    await cb.answer()


@router.message(TeacherAdd.photo, F.photo)
async def get_teacher_photo(message: Message, state: FSMContext):
    await state.update_data(photo=message.photo[-1].file_id)
    await state.set_state(TeacherAdd.subject)
    await message.answer("2/3. Qaysi <b>fandan</b> dars beradi?")


@router.message(TeacherAdd.photo)
async def teacher_photo_invalid(message: Message):
    await message.answer("Iltimos, rasm yuboring.")


@router.message(TeacherAdd.subject, F.text)
async def get_teacher_subject(message: Message, state: FSMContext):
    subject = message.text.strip()
    if not 2 <= len(subject) <= 100:
        await message.answer("Fan nomini 2 tadan 100 tagacha belgida yozing:")
        return
    await state.update_data(subject=subject)
    await state.set_state(TeacherAdd.certificate)
    await message.answer("3/3. Fan bo'yicha <b>sertifikat rasmini</b> yuboring (bo'lsa):", reply_markup=skip_cert_kb())


@router.message(TeacherAdd.certificate, F.photo)
async def get_teacher_certificate(message: Message, state: FSMContext, api: ApiClient):
    await state.update_data(certificate=message.photo[-1].file_id)
    await _finish_add_teacher(message, state, api)


@router.callback_query(TeacherAdd.certificate, TeacherFlowCB.filter(F.action == "skipcert"))
async def skip_teacher_certificate(cb: CallbackQuery, state: FSMContext, api: ApiClient):
    await state.update_data(certificate=None)
    await cb.message.edit_text("Sertifikat: yo'q")
    await _finish_add_teacher(cb.message, state, api)
    await cb.answer()


async def _finish_add_teacher(message: Message, state: FSMContext, api: ApiClient):
    data = await state.get_data()
    try:
        result = await admin_api.add_teacher(api, message.from_user.id, {
            "userId": data["user_id"], "subject": data["subject"],
            "photo": data.get("photo"), "certificate": data.get("certificate"),
        })
    except ApiError as e:
        await message.answer(e.message)
        await state.clear()
        return
    await state.clear()
    await message.answer(f"🎉 <b>{escape(result['fullName'])}</b> endi o'qituvchi!")