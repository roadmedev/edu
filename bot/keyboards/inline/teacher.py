from aiogram.types import InlineKeyboardButton as Btn, InlineKeyboardMarkup as Markup

from callbacks.teacher import DayCB, FlowCB, MyCourseCB
from utils.formatters import WEEKDAYS


def _flow(text: str, action: str) -> Btn:
    return Btn(text=text, callback_data=FlowCB(action=action).pack())


def my_course_kb(course_id: int, has_cert: bool) -> Markup:
    row = []
    if has_cert:
        row.append(Btn(text="📜 Sertifikat", callback_data=MyCourseCB(action="cert", course_id=course_id).pack()))
    row.append(Btn(text="🗑 O'chirish", callback_data=MyCourseCB(action="del", course_id=course_id).pack()))
    return Markup(inline_keyboard=[row])


def confirm_delete_kb(course_id: int) -> Markup:
    return Markup(inline_keyboard=[[
        Btn(text="✅ Ha, o'chirish", callback_data=MyCourseCB(action="delyes", course_id=course_id).pack()),
        Btn(text="↩️ Yo'q", callback_data=MyCourseCB(action="delno", course_id=course_id).pack()),
    ]])


def cancel_kb() -> Markup:
    return Markup(inline_keyboard=[[_flow("❌ Bekor qilish", "cancel")]])


def skip_cert_kb() -> Markup:
    return Markup(inline_keyboard=[
        [_flow("Sertifikatim yo'q", "skipcert")],
        [_flow("❌ Bekor qilish", "cancel")],
    ])


def days_kb(taken: set[int]) -> Markup:
    buttons = [
        Btn(text=WEEKDAYS[d].capitalize(), callback_data=DayCB(day=d).pack())
        for d in range(1, 8) if d not in taken
    ]
    rows = [buttons[i:i + 2] for i in range(0, len(buttons), 2)]
    rows.append([_flow("❌ Bekor qilish", "cancel")])
    return Markup(inline_keyboard=rows)


def conflict_kb() -> Markup:
    return Markup(inline_keyboard=[
        [_flow("🗓 Dars jadvalini ko'rish", "timetable")],
        [_flow("🔁 Boshqa vaqt kiritish", "retry")],
        [_flow("❌ Bekor qilish", "cancel")],
    ])


def schedule_actions_kb(can_add: bool) -> Markup:
    rows = []
    if can_add:
        rows.append([_flow("➕ Kun qo'shish", "addday")])
    rows.append([_flow("✅ Saqlash", "save"), _flow("❌ Bekor qilish", "cancel")])
    return Markup(inline_keyboard=rows)