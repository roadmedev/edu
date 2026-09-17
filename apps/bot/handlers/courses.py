from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

from services.courses_service import get_courses, get_course_detail, enroll_in_course
from keyboards.courses_kb import get_courses_keyboard, get_enroll_keyboard

router = Router()


@router.message(F.text == "📚 Kurslar")
async def show_courses(message: Message) -> None:
    courses = await get_courses()

    if not courses:
        await message.answer("Hozircha kurslar mavjud emas.")
        return

    await message.answer("Mavjud kurslar:", reply_markup=get_courses_keyboard(courses))


@router.callback_query(F.data.startswith("course:"))
async def show_course_detail(callback: CallbackQuery) -> None:
    course_id = callback.data.split(":")[1]
    course = await get_course_detail(course_id)

    if "error" in course:
        await callback.answer("Kurs topilmadi", show_alert=True)
        return

    course = course["course"]
    text = (
        f"📚 <b>{course['title']}</b>\n\n"
        f"{course.get('description') or ''}\n\n"
        f"💵 Narxi: {course.get('price') or 0} so'm\n\n"
        f"👨‍🏫 O'qituvchi: {course.get('teacher_name') or '—'}\n"
        f"Daraja: {course.get('teacher_degree') or '—'}\n"
        f"Sertifikat: {course.get('teacher_certificate') or '—'}"
    )

    await callback.message.answer(text, parse_mode="HTML", reply_markup=get_enroll_keyboard(course_id))
    await callback.answer()


@router.callback_query(F.data.startswith("enroll:"))
async def handle_enroll(callback: CallbackQuery) -> None:
    course_id = callback.data.split(":")[1]
    result = await enroll_in_course(callback.from_user.id, course_id)

    if result.get("already_enrolled"):
        await callback.answer("Siz bu kursga allaqachon yozilgansiz.", show_alert=True)
        return

    if "error" in result:
        await callback.answer("Xatolik yuz berdi, qayta urinib ko'ring.", show_alert=True)
        return

    await callback.message.answer(
        "✅ Siz kursga muvaffaqiyatli yozildingiz! Markaz siz bilan tez orada bog'lanadi."
    )
    await callback.answer()