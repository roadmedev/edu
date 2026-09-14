from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

from services.courses_service import get_courses
from keyboards.courses_kb import get_courses_keyboard

router = Router()

@router.message(F.text == "📚 Kurslar")
async def show_courses(message: Message) -> None:
    courses = await get_courses()

    if not courses:
        await message.answer("Hozircha kurslar mavjud emas.")
        return
    
    await message.answer(
        "Mavjud kurslar:", 
        reply_markup=get_courses_keyboard(courses),
    )


@router.callback_query(F.data.startswith("course:"))
async def show_course_detail(callback: CallbackQuery) -> None:
    course_id = callback.data.split(":")[1]
    courses = await get_courses()
    course = next((c for c in courses if str(c["id"]) == course_id), None)

    if not course:
        await callback.answer("Kurs topilmadi", show_alert=True)
        return

    await callback.message.answer(
        f"📚 {course['title']}\n\n{course['description']}"
    )
    await callback.answer() # Telegram'ga "tugma bosilishi qayta ishlandi" deb bildiradi