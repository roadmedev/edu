from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def get_phone_keyboard() -> ReplyKeyboardMarkup:
    """Telefon raqamni yuborish uchun klaviatura"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📱 Telefon raqamni yuborish", request_contact=True)]
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )