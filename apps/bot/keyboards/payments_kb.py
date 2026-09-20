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


def get_debtors_keyboard(debtors: list[dict]) -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(
                text=f"💳 {d['full_name']} — {d['course_title']} to'lovini qayd etish",
                callback_data=f"mark_paid:{d['enrollment_id']}",
            )
        ]
        for d in debtors
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)