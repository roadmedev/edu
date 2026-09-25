from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from callbacks.courses import JoinCB


def join_keyboard(course_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="✅ Kursga qo'shilish", callback_data=JoinCB(course_id=course_id).pack())
    ]])