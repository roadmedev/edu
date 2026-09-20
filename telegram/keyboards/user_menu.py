# keyboards/user_menu.py
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def get_user_menu() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📚 Kurslar")],
            [
                KeyboardButton(text="📖 Mening"),
                KeyboardButton(text="📅 Dars jadvali"),
                KeyboardButton(text="⭐ Reyting"),
            ],
            [KeyboardButton(text="ℹ️ Yordam")],
        ],
        resize_keyboard=True,
    )