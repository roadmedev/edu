from aiogram.types import InlineKeyboardButton as Btn, InlineKeyboardMarkup as Markup

from callbacks.enrollments import EnrollCB


def request_kb(eid: int) -> Markup:
    return Markup(inline_keyboard=[[
        Btn(text="✅ Qabul qilish", callback_data=EnrollCB(action="accept", enrollment_id=eid).pack()),
        Btn(text="❌ Rad qilish", callback_data=EnrollCB(action="reject", enrollment_id=eid).pack()),
    ]])


def terms_kb(eid: int) -> Markup:
    return Markup(inline_keyboard=[[
        Btn(text="📄 Shartlarni qabul qilish", callback_data=EnrollCB(action="terms", enrollment_id=eid).pack()),
    ]])