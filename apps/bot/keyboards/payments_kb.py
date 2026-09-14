from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_payments_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ To'lov qilganlar", callback_data="payments:paid"),
                InlineKeyboardButton(text="❗ Qarzdorlar", callback_data="payments:debtors"),
            ]
        ]
    )