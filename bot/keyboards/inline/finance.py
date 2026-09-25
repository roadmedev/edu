from aiogram.types import InlineKeyboardButton as Btn, InlineKeyboardMarkup as Markup

from callbacks.finance import PayoutCB


def payout_kb(teacher_id: int) -> Markup:
    return Markup(inline_keyboard=[[
        Btn(text="✅ To'ladi", callback_data=PayoutCB(action="full", teacher_id=teacher_id).pack()),
        Btn(text="🟡 Qisman", callback_data=PayoutCB(action="partial", teacher_id=teacher_id).pack()),
    ]])


def review_teachers_kb() -> Markup:
    return Markup(inline_keyboard=[[Btn(text="📋 O'qituvchilar ulushi", callback_data="finance_review")]])