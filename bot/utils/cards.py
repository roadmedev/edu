from aiogram.types import Message

from utils.formatters import format_course


async def send_course_card(message: Message, course: dict, kb=None):
    text = format_course(course)
    photo = course.get("photo") or course.get("teacherPhoto")
    if photo:
        await message.answer_photo(photo, caption=text, reply_markup=kb)
    else:
        await message.answer(text, reply_markup=kb)