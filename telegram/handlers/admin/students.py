# handlers/admin/students.py
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

from services.admin_service import (
    get_subjects,
    get_groups_by_subject,
    get_students_by_group,
    get_student_detail,
    get_students,
)
from keyboards.students_kb import build_list_keyboard
from utils.filters import IsAdmin

router = Router()
router.message.filter(IsAdmin())
router.callback_query.filter(IsAdmin())


@router.message(F.text == "🎓 O'quvchilar")
async def show_subjects(message: Message) -> None:
    """Fan → Guruh → O'quvchi navigatsiyasi"""
    subjects = await get_subjects()

    if not subjects:
        await message.answer("Hozircha fanlar mavjud emas.")
        return

    await message.answer(
        "📚 Fanni tanlang:",
        reply_markup=build_list_keyboard(subjects, prefix="stu_subject"),
    )


@router.callback_query(F.data.startswith("stu_subject:"))
async def show_groups(callback: CallbackQuery) -> None:
    subject_id = int(callback.data.split(":")[1])
    groups = await get_groups_by_subject(subject_id)

    if not groups:
        await callback.message.answer("Bu fan bo'yicha guruhlar yo'q.")
        await callback.answer()
        return

    await callback.message.edit_text(
        "👥 Guruhni tanlang:",
        reply_markup=build_list_keyboard(groups, prefix="stu_group"),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("stu_group:"))
async def show_group_students(callback: CallbackQuery) -> None:
    group_id = int(callback.data.split(":")[1])
    students = await get_students_by_group(group_id)

    if not students:
        await callback.message.answer("Bu guruhda o'quvchilar yo'q.")
        await callback.answer()
        return

    await callback.message.edit_text(
        "🎓 O'quvchini tanlang:",
        reply_markup=build_list_keyboard(students, prefix="stu_detail", label_key="full_name"),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("stu_detail:"))
async def show_student_detail(callback: CallbackQuery) -> None:
    student_id = int(callback.data.split(":")[1])
    student = await get_student_detail(student_id)

    if "error" in student:
        await callback.answer("O'quvchi topilmadi", show_alert=True)
        return

    enrollments_text = "\n".join(
        f"  • {e['title']} — {e['status']}"
        for e in student.get("enrollments", [])
    ) or "  Kurslarga yozilmagan"

    grades_text = "\n".join(
        f"  • {g['course_title']}: <b>{g['grade']}</b>"
        for g in student.get("grades", [])
    ) or "  Baholar yo'q"

    text = (
        f"🎓 <b>{student['full_name']}</b>\n\n"
        f"📱 Telefon: {student['phone_number']}\n"
        f"📅 Ro'yxatdan: {student.get('created_at', '—')[:10]}\n\n"
        f"<b>Kurslar:</b>\n{enrollments_text}\n\n"
        f"<b>Baholar:</b>\n{grades_text}"
    )

    await callback.message.edit_text(text, parse_mode="HTML")
    await callback.answer()