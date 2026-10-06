from aiogram.types import InlineKeyboardButton as Btn, InlineKeyboardMarkup as Markup

from callbacks.admin import CandidateCB, StudentAdminCB, TeacherAdminCB, TeacherFlowCB
from utils import labels as L

from callbacks.broadcast import BroadcastCB

#def add_teacher_kb() -> Markup:
#    return Markup(inline_keyboard=[[Btn(text=L.ADD_TEACHER, callback_data="admin_add_teacher")]])


def teacher_card_kb(teacher_id: int) -> Markup:
    return Markup(inline_keyboard=[[
        Btn(text="📚 Kurslarini ko'rish", callback_data=TeacherAdminCB(action="view", teacher_id=teacher_id).pack()),
        Btn(text="🗑 O'chirish", callback_data=TeacherAdminCB(action="del", teacher_id=teacher_id).pack()),
    ]])


def confirm_delete_teacher_kb(teacher_id: int) -> Markup:
    return Markup(inline_keyboard=[[
        Btn(text="✅ Ha", callback_data=TeacherAdminCB(action="delyes", teacher_id=teacher_id).pack()),
        Btn(text="↩️ Yo'q", callback_data=TeacherAdminCB(action="delno", teacher_id=teacher_id).pack()),
    ]])


def candidates_kb(candidates: list[dict]) -> Markup:
    return Markup(inline_keyboard=[
        [Btn(text=f"{c['fullName']} (id{c['id']})", callback_data=CandidateCB(user_id=c["id"]).pack())]
        for c in candidates
    ])


def skip_cert_kb() -> Markup:
    return Markup(inline_keyboard=[[Btn(text="Sertifikati yo'q", callback_data=TeacherFlowCB(action="skipcert").pack())]])


def student_list_kb(students: list[dict]) -> Markup:
    rows = [
        [Btn(text=s["studentName"], callback_data=StudentAdminCB(action="view", enrollment_id=s["enrollmentId"]).pack())]
        for s in students
    ]
    rows.append([Btn(text=L.BROADCAST, callback_data=BroadcastCB(action="start", target="students").pack())])
    return Markup(inline_keyboard=rows)


def student_detail_kb(enrollment_id: int, paid: bool) -> Markup:
    rows = []
    if not paid:
        rows.append([
            Btn(text="✅ To'lovni bajardi", callback_data=StudentAdminCB(action="paid", enrollment_id=enrollment_id).pack()),
            Btn(text="📨 So'rov yuborish", callback_data=StudentAdminCB(action="remind", enrollment_id=enrollment_id).pack()),
        ])
    rows.append([Btn(text="🔙 Orqaga", callback_data=StudentAdminCB(action="back", enrollment_id=0).pack())])
    return Markup(inline_keyboard=rows)

def teachers_header_kb() -> Markup:
    return Markup(inline_keyboard=[
        [Btn(text=L.ADD_TEACHER, callback_data="admin_add_teacher")],
        [Btn(text=L.BROADCAST, callback_data=BroadcastCB(action="start", target="teachers").pack())],
    ])