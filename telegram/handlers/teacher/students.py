# handlers/teacher/students.py
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from services.teacher_service import (
    get_teacher_students,
    mark_payment,
    set_grade,
)
from keyboards.students_kb import build_list_keyboard
from utils.filters import IsTeacher

router = Router()
router.message.filter(IsTeacher())
router.callback_query.filter(IsTeacher())


@router.message(F.text == "👥 O'quvchilarim")
async def show_students(message: Message) -> None:
    students = await get_teacher_students(message.from_user.id)

    if not students:
        await message.answer("Hozircha o'quvchilaringiz yo'q.")
        return

    # Kurslar bo'yicha guruhlash
    by_course = {}
    for s in students:
        course_title = s["course_title"]
        if course_title not in by_course:
            by_course[course_title] = []
        by_course[course_title].append(s)

    text = "👥 <b>O'quvchilarim</b>\n\n"
    for course_title, course_students in by_course.items():
        text += f"📚 <b>{course_title}</b>\n"
        for s in course_students:
            status_emoji = "✅" if s["status"] == "active" else "⚠️"
            grade_text = f" · ⭐ {s['last_grade']}" if s.get("last_grade") else ""
            text += f"  {status_emoji} {s['full_name']}{grade_text}\n"
        text += "\n"

    await message.answer(text, parse_mode="HTML")

    # Inline tugmalar (student tanlash)
    await message.answer(
        "O'quvchi ustiga bosib, ma'lumotni ko'ring:",
        reply_markup=build_list_keyboard(students, prefix="t_student", label_key="full_name"),
    )


@router.callback_query(F.data.startswith("t_student:"))
async def show_student_detail(callback: CallbackQuery) -> None:
    student_id = int(callback.data.split(":")[1])

    # O'quvchilar ro'yxatidan topamiz
    students = await get_teacher_students(callback.from_user.id)
    student = next((s for s in students if s["id"] == student_id), None)

    if not student:
        await callback.answer("Topilmadi", show_alert=True)
        return

    status_label = {
        "active": "✅ To'lagan",
        "qarzdor": "⚠️ Qarzdor",
        "completed": "🎓 Tugatgan",
        "cancelled": "❌ Bekor qilingan",
    }.get(student["status"], student["status"])

    text = (
        f"🎓 <b>{student['full_name']}</b>\n\n"
        f"📱 Telefon: {student.get('phone_number', '—')}\n"
        f"📚 Kurs: {student['course_title']}\n"
        f"📊 Holat: {status_label}\n"
        f"⭐ Oxirgi baho: {student.get('last_grade', '—')}\n"
        f"📅 Yozilgan: {student.get('enrolled_at', '—')[:10]}"
    )

    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    buttons = []

    # To'lov tugmasi (faqat qarzdorlar uchun)
    if student["status"] == "qarzdor":
        buttons.append([
            InlineKeyboardButton(
                text="💰 To'ladi",
                callback_data=f"t_payment:{student['id']}:{student['course_id']}",
            )
        ])

    # Baho qo'yish
    buttons.append([
        InlineKeyboardButton(
            text="⭐ Baho qo'yish",
            callback_data=f"t_grade:{student['id']}:{student['course_id']}",
        )
    ])

    await callback.message.edit_text(
        text,
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("t_payment:"))
async def mark_student_payment(callback: CallbackQuery) -> None:
    _, student_id, course_id = callback.data.split(":")
    student_id = int(student_id)
    course_id = int(course_id)

    # Kurs narxini olish
    students = await get_teacher_students(callback.from_user.id)
    student = next(
        (s for s in students if s["id"] == student_id and s["course_id"] == course_id),
        None,
    )

    if not student:
        await callback.answer("Topilmadi", show_alert=True)
        return

    # To'lovni belgilash (narx student'da bo'lishi kerak)
    amount = student.get("price", 0)
    if not amount:
        await callback.answer("Kurs narxi topilmadi", show_alert=True)
        return

    result = await mark_payment(
        callback.from_user.id,
        student_id,
        course_id,
        float(amount),
    )

    if "error" in result:
        await callback.answer(f"Xatolik: {result['error']}", show_alert=True)
        return

    await callback.message.edit_text(
        f"✅ <b>{student['full_name']}</b> to'lovi qayd etildi!\n"
        f"💰 {amount} so'm",
        parse_mode="HTML",
    )
    await callback.answer("Saqlandi")