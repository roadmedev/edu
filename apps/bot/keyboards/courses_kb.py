from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_courses_keyboard(courses: list[dict]) -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text=course["title"], callback_data=f"course:{'id'}")]
        for course in courses
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)