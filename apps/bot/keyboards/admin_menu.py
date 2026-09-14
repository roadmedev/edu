from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def get_admin_menu() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📊 Markaz statistikasi")],
            [KeyboardButton(text="💰 Moliya bo'limi")],
            [KeyboardButton(text="👨‍🏫 O'qituvchilar")],
            [KeyboardButton(text="🎓 O'quvchilar")],
            [KeyboardButton(text="💳 To'lovlar")],
        ],
        resize_keyboard=True,
    )