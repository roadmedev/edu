# handlers/teacher/profile.py
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from services.teacher_service import (
    get_teacher_profile,
    get_my_courses,
    update_teacher_profile,
)
from keyboards.teachers_kb import (
    get_profile_keyboard,
    get_edit_field_keyboard,
    get_courses_list_keyboard,
)
from states.teacher_course import EditProfile
from utils.filters import IsTeacher

router = Router()
router.message.filter(IsTeacher())
router.callback_query.filter(IsTeacher())


@router.message(F.text == "👤 Mening")
async def show_profile(message: Message) -> None:
    result = await get_teacher_profile(message.from_user.id)
    if "error" in result:
        await message.answer("⚠️ Profilni yuklashda xatolik.")
        return
    teacher = result.get("teacher", {})
    text = (
        f"👨‍🏫 <b>{teacher.get('full_name', '—')}</b>\n\n"
        f"📚 Fan: {teacher.get('subject_name') or '—'}\n"
        f"🎓 Daraja: {teacher.get('degree') or '—'}\n"
        f"📜 Sertifikat: {teacher.get('certificate_info') or '—'}\n"
        f"💵 Maosh: {teacher.get('salary') or 0} so'm\n"
    )
    if teacher.get("photo_url"):
        try:
            await message.answer_photo(
                photo=teacher["photo_url"],
                caption=text,
                parse_mode="HTML",
                reply_markup=get_profile_keyboard(),
            )
        except Exception:
            await message.answer(text, parse_mode="HTML", reply_markup=get_profile_keyboard())
    else:
        await message.answer(text, parse_mode="HTML", reply_markup=get_profile_keyboard())
    courses = await get_my_courses(message.from_user.id)
    if courses:
        await message.answer(
            f"📚 <b>Mening kurslarim</b> ({len(courses)} ta):",
            parse_mode="HTML",
            reply_markup=get_courses_list_keyboard(courses),
        )
    else:
        await message.answer("📚 Hozircha kurslaringiz yo'q. ➕ Yangi kurs qo'shish tugmasini bosing.")


@router.callback_query(F.data == "profile_edit")
async def start_edit_profile(callback: CallbackQuery) -> None:
    await callback.message.answer(
        "✏️ Qaysi maydonni tahrirlaysiz?",
        reply_markup=get_edit_field_keyboard(),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("profile_edit_field:"))
async def choose_edit_field(callback: CallbackQuery, state: FSMContext) -> None:
    field = callback.data.split(":")[1]
    await state.update_data(field=field)
    await state.set_state(EditProfile.waiting_for_new_value)
    await callback.message.answer("✏️ Yangi qiymatni kiriting:")
    await callback.answer()


@router.message(EditProfile.waiting_for_new_value)
async def save_edit_field(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    await state.clear()
    result = await update_teacher_profile(
        message.from_user.id,
        data["field"],
        message.text,
    )
    if "error" in result:
        await message.answer("⚠️ Xatolik yuz berdi.")
        return
    await message.answer("✅ Yangilandi!")