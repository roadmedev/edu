# keyboards/teacher_menu.py
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def get_teacher_menu() -> ReplyKeyboardMarkup:
    """Teacher asosiy menyusi"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="👤 Mening")],
            [
                KeyboardButton(text="👥 O'quvchilarim"),
                KeyboardButton(text="💰 Balans"),
            ],
            [KeyboardButton(text="💡 Taklif")],
        ],
        resize_keyboard=True,
    )