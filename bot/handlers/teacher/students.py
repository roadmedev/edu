from aiogram import F, Router
from aiogram.types import CallbackQuery, Message

from api import courses as courses_api, payments as payments_api, students as students_api
from api.client import ApiClient, ApiError
from callbacks.students import MyStudentsCB
from filters.role import RoleFilter
from keyboards.inline.students import course_pick_kb, student_detail_kb, student_list_kb
from utils import labels as L
from utils.formatters import format_student_detail, format_student_list_header

router = Router(name="teacher_students")
router.message.filter(RoleFilter("teacher"))
router.callback_query.filter(RoleFilter("teacher"))


async def _render_list(target, api: ApiClient, tg_id: int, course_id: int, edit: bool):
    data = await students_api.course_students(api, tg_id, course_id)
    if not data["students"]:
        text, kb = f"📚 <b>{data['courseTitle']}</b>\n\nHozircha o'quvchi yo'q.", None
    else:
        text, kb = format_student_list_header(data), student_list_kb(course_id, data["students"])
    await (target.edit_text(text, reply_markup=kb) if edit else target.answer(text, reply_markup=kb))


@router.message(F.text == L.MY_STUDENTS)
async def students_entry(message: Message, api: ApiClient):
    courses = await courses_api.my_courses(api, message.from_user.id)
    if not courses:
        await message.answer("Sizda hali kurs yo'q.")
        return
    if len(courses) == 1:
        await _render_list(message, api, message.from_user.id, courses[0]["id"], edit=False)
        return
    await message.answer("Qaysi kurs o'quvchilarini ko'rmoqchisiz?", reply_markup=course_pick_kb(courses))


@router.callback_query(MyStudentsCB.filter(F.action == "course"))
async def pick_course(cb: CallbackQuery, callback_data: MyStudentsCB, api: ApiClient):
    await _render_list(cb.message, api, cb.from_user.id, callback_data.course_id, edit=True)
    await cb.answer()


@router.callback_query(MyStudentsCB.filter(F.action == "back"))
async def back_to_list(cb: CallbackQuery, callback_data: MyStudentsCB, api: ApiClient):
    await _render_list(cb.message, api, cb.from_user.id, callback_data.course_id, edit=True)
    await cb.answer()


@router.callback_query(MyStudentsCB.filter(F.action == "student"))
async def show_detail(cb: CallbackQuery, callback_data: MyStudentsCB, api: ApiClient):
    data = await students_api.course_students(api, cb.from_user.id, callback_data.course_id)
    s = next((x for x in data["students"] if x["enrollmentId"] == callback_data.enrollment_id), None)
    if not s:
        await cb.answer("Topilmadi", show_alert=True)
        return
    await cb.message.edit_text(
        format_student_detail(data["courseTitle"], s),
        reply_markup=student_detail_kb(callback_data.course_id, callback_data.enrollment_id, s["status"] == "paid"),
    )
    await cb.answer()


@router.callback_query(MyStudentsCB.filter(F.action == "pay"))
async def mark_paid(cb: CallbackQuery, callback_data: MyStudentsCB, api: ApiClient):
    try:
        await payments_api.mark_paid(api, cb.from_user.id, callback_data.enrollment_id)
    except ApiError as e:
        await cb.answer(e.message, show_alert=True)
        return

    data = await students_api.course_students(api, cb.from_user.id, callback_data.course_id)
    s = next((x for x in data["students"] if x["enrollmentId"] == callback_data.enrollment_id), None)
    await cb.message.edit_text(
        format_student_detail(data["courseTitle"], s),
        reply_markup=student_detail_kb(callback_data.course_id, callback_data.enrollment_id, True),
    )
    await cb.answer("✅ To'lov qayd etildi")