from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


def build(*rows: tuple[str, ...]) -> ReplyKeyboardMarkup:
    """Har bir tuple bitta qator. Menyu yig'ishning yagona joyi."""
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=t) for t in row] for row in rows],
        resize_keyboard=True,
    )


def phone_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="📱 Raqamni yuborish", request_contact=True)]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )