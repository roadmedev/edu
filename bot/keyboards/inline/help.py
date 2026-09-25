from aiogram.types import InlineKeyboardButton as Btn, InlineKeyboardMarkup as Markup

from config import settings


def help_kb() -> Markup:
    return Markup(inline_keyboard=[[
        Btn(text=f"👨‍💻 Administrator: @{settings.admin_username}",
            url=f"https://t.me/{settings.admin_username}")
    ]])