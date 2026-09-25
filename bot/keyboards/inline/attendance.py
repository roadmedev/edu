from aiogram.types import InlineKeyboardButton as Btn, InlineKeyboardMarkup as Markup

from callbacks.attendance import AttendanceCB


def attendance_kb(course_id: int, students: list[dict], state: dict[int, bool]) -> Markup:
    rows = []
    for s in students:
        present = state.get(s["enrollmentId"], True)
        mark = "✅ Keldi" if present else "❌ Kelmadi"
        rows.append([Btn(text=f"{s['studentName']}: {mark}",
                          callback_data=AttendanceCB(action="toggle", course_id=course_id, enrollment_id=s["enrollmentId"]).pack())])
    rows.append([Btn(text="💾 Saqlash", callback_data=AttendanceCB(action="save", course_id=course_id).pack())])
    return Markup(inline_keyboard=rows)