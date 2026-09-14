from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_finance_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="📥 Kirimlar tarixi", callback_data="finance_history:income"),
                InlineKeyboardButton(text="📤 Chiqimlar tarixi", callback_data="finance_history:expense"),
            ]
        ]
    )