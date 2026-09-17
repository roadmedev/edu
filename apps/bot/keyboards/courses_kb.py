from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_courses_keyboard(courses: list[dict]) -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text=course["title"], callback_data=f"course:{course['id']}")]
        for course in courses
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_enroll_keyboard(course_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ Kursga yozilish", callback_data=f"enroll:{course_id}")]
        ]
    )