from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from services.teachers_service import (
    get_teachers,
    get_teacher_detail,
    create_teacher,
    update_teacher_field,
    delete_teacher,
)
from services.students_service import get_subjects
from keyboards.teachers_kb import (
    get_teachers_keyboard,
    get_teacher_detail_keyboard,
    get_edit_field_keyboard,
    get_delete_confirm_keyboard,
)
from keyboards.students_kb import build_list_keyboard
from states.teacher_admin import AddTeacher, EditTeacher

router = Router()


# --- Ro'yxat va tafsilot (avvalgi kod, ozgina o'zgargan) ---

@router.message(F.text == "👨‍🏫 O'qituvchilar")
async def show_teachers(message: Message) -> None:
    teachers = await get_teachers()
    await message.answer(
        "O'qituvchilar ro'yxati:" if teachers else "Hozircha o'qituvchilar yo'q, birinchisini qo'shing:",
        reply_markup=get_teachers_keyboard(teachers),
    )


@router.callback_query(F.data.startswith("teacher:"))
async def show_teacher_detail(callback: CallbackQuery) -> None:
    teacher_id = callback.data.split(":")[1]
    teacher = await get_teacher_detail(teacher_id)

    if "error" in teacher:
        await callback.answer("O'qituvchi topilmadi", show_alert=True)
        return

    text = (
        f"👨‍🏫 <b>{teacher['full_name']}</b>\n\n"
        f"Fan: {teacher.get('subject_name') or '—'}\n"
        f"Daraja: {teacher.get('degree') or '—'}\n"
        f"Sertifikat: {teacher.get('certificate_info') or '—'}\n"
        f"Maosh: {teacher.get('salary') or 0} so'm\n\n"
        f"Guruhlar soni: {teacher['groups_count']}\n"
        f"O'quvchilar soni: {teacher['students_count']}"
    )
    await callback.message.answer(text, parse_mode="HTML", reply_markup=get_teacher_detail_keyboard(teacher_id))
    await callback.answer()


# --- Qo'shish (FSM) ---

@router.callback_query(F.data == "teacher_add")
async def start_add_teacher(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(AddTeacher.waiting_for_name)
    await callback.message.answer("Yangi o'qituvchining to'liq ismini kiriting:")
    await callback.answer()


@router.message(AddTeacher.waiting_for_name)
async def add_teacher_name(message: Message, state: FSMContext) -> None:
    await state.update_data(full_name=message.text)
    await state.set_state(AddTeacher.waiting_for_degree)
    await message.answer("Darajasini kiriting (masalan: \"Katta o'qituvchi\"):")


@router.message(AddTeacher.waiting_for_degree)
async def add_teacher_degree(message: Message, state: FSMContext) -> None:
    await state.update_data(degree=message.text)
    subjects = await get_subjects()
    await state.set_state(AddTeacher.waiting_for_subject)
    await message.answer(
        "Fanni tanlang:",
        reply_markup=build_list_keyboard(subjects, prefix="add_teacher_subject"),
    )


@router.callback_query(AddTeacher.waiting_for_subject, F.data.startswith("add_teacher_subject:"))
async def add_teacher_subject(callback: CallbackQuery, state: FSMContext) -> None:
    subject_id = callback.data.split(":")[1]
    await state.update_data(subject_id=int(subject_id))
    await state.set_state(AddTeacher.waiting_for_certificate)
    await callback.message.answer("Sertifikat haqida ma'lumot kiriting (yoki \"-\" deb yozing, agar yo'q bo'lsa):")
    await callback.answer()


@router.message(AddTeacher.waiting_for_certificate)
async def add_teacher_certificate(message: Message, state: FSMContext) -> None:
    await state.update_data(certificate_info=message.text)
    await state.set_state(AddTeacher.waiting_for_salary)
    await message.answer("Oylik maoshini kiriting (faqat son, masalan: 4500000):")


@router.message(AddTeacher.waiting_for_salary)
async def add_teacher_salary(message: Message, state: FSMContext) -> None:
    try:
        salary = float(message.text)
    except ValueError:
        await message.answer("Iltimos, faqat son kiriting (masalan: 4500000):")
        return

    data = await state.update_data(salary=salary)
    await state.clear()

    result = await create_teacher(data)

    if "error" in result:
        await message.answer("Xatolik yuz berdi, qayta urinib ko'ring.")
        return

    await message.answer(f"✅ {result['teacher']['full_name']} muvaffaqiyatli qo'shildi!")


# --- Tahrirlash ---

@router.callback_query(F.data.startswith("teacher_edit:"))
async def start_edit_teacher(callback: CallbackQuery) -> None:
    teacher_id = callback.data.split(":")[1]
    await callback.message.answer(
        "Qaysi maydonni tahrirlaysiz?",
        reply_markup=get_edit_field_keyboard(teacher_id),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("teacher_edit_field:"))
async def choose_edit_field(callback: CallbackQuery, state: FSMContext) -> None:
    _, teacher_id, field = callback.data.split(":")
    await state.update_data(teacher_id=teacher_id, field=field)
    await state.set_state(EditTeacher.waiting_for_new_value)
    await callback.message.answer("Yangi qiymatni kiriting:")
    await callback.answer()


@router.message(EditTeacher.waiting_for_new_value)
async def save_edit_field(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    await state.clear()

    result = await update_teacher_field(data["teacher_id"], data["field"], message.text)

    if "error" in result:
        await message.answer("Xatolik yuz berdi, qayta urinib ko'ring.")
        return

    await message.answer(f"✅ Yangilandi: {result['teacher']['full_name']}")


# --- O'chirish ---

@router.callback_query(F.data.startswith("teacher_delete:"))
async def confirm_delete_teacher(callback: CallbackQuery) -> None:
    teacher_id = callback.data.split(":")[1]
    await callback.message.answer(
        "Rostdan ham bu o'qituvchini o'chirmoqchimisiz?",
        reply_markup=get_delete_confirm_keyboard(teacher_id),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("teacher_delete_confirm:"))
async def do_delete_teacher(callback: CallbackQuery) -> None:
    teacher_id = callback.data.split(":")[1]
    await delete_teacher(teacher_id)
    await callback.message.answer("🗑 O'qituvchi o'chirildi.")
    await callback.answer()


@router.callback_query(F.data == "teacher_delete_cancel")
async def cancel_delete_teacher(callback: CallbackQuery) -> None:
    await callback.message.answer("Bekor qilindi.")
    await callback.answer()