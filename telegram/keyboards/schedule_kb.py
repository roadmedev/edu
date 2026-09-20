# keyboards/schedule_kb.py
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


DAYS = {
    1: "Dushanba",
    2: "Seshanba",
    3: "Chorshanba",
    4: "Payshanba",
    5: "Juma",
    6: "Shanba",
    7: "Yakshanba",
}


def get_days_keyboard(course_id: int) -> InlineKeyboardMarkup:
    """Hafta kunlari"""
    buttons = []
    row = []
    for day_num, day_name in DAYS.items():
        row.append(
            InlineKeyboardButton(
                text=day_name,
                callback_data=f"sched_day:{course_id}:{day_num}",
            )
        )
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_schedule_actions_keyboard(course_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="➕ Yana kun qo'shish",
                    callback_data=f"sched_more:{course_id}",
                ),
                InlineKeyboardButton(
                    text="✅ Tayyor",
                    callback_data="sched_done",
                ),
            ]
        ]
    )