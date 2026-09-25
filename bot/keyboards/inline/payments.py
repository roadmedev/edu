from aiogram.types import InlineKeyboardButton as Btn, InlineKeyboardMarkup as Markup

from callbacks.payments import PayCB


def payment_request_kb(enrollment_id: int) -> Markup:
    return Markup(inline_keyboard=[[
        Btn(text="✅ To'ladi", callback_data=PayCB(action="full", enrollment_id=enrollment_id).pack()),
        Btn(text="🟡 Qisman", callback_data=PayCB(action="partial", enrollment_id=enrollment_id).pack()),
    ]])


def review_students_kb() -> Markup:
    return Markup(inline_keyboard=[[Btn(text="📋 O'quvchilar to'lovlari", callback_data="balance_review")]])
