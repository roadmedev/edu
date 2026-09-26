from aiogram.types import InlineKeyboardButton as Btn, InlineKeyboardMarkup as Markup

from callbacks.students import MyStudentsCB
from callbacks.attendance import AttendanceCB
from utils import labels as L
from callbacks.attendance import AttendanceCB


def course_pick_kb(courses: list[dict]) -> Markup:
    return Markup(inline_keyboard=[
        [Btn(text=c["title"], callback_data=MyStudentsCB(action="course", course_id=c["id"]).pack())]
        for c in courses
    ])


def student_list_kb(course_id: int, students: list[dict]) -> Markup:
    return Markup(inline_keyboard=[
        [Btn(text=s["studentName"], callback_data=MyStudentsCB(action="student", course_id=course_id, enrollment_id=s["enrollmentId"]).pack())]
        for s in students
    ])


def student_detail_kb(course_id: int, enrollment_id: int, paid: bool) -> Markup:
    rows = []
    if not paid:
        rows.append([Btn(text="✅ To'ladi", callback_data=MyStudentsCB(action="pay", course_id=course_id, enrollment_id=enrollment_id).pack())])
    rows.append([Btn(text="🔙 Orqaga", callback_data=MyStudentsCB(action="back", course_id=course_id).pack())])
    return Markup(inline_keyboard=rows)

def student_list_kb(course_id: int, students: list[dict]) -> Markup:
    rows = [
        [Btn(text=s["studentName"], callback_data=MyStudentsCB(action="student", course_id=course_id, enrollment_id=s["enrollmentId"]).pack())]
        for s in students
    ]
    rows.append([Btn(text=L.ATTENDANCE, callback_data=AttendanceCB(action="start", course_id=course_id).pack())])
    return Markup(inline_keyboard=rows)