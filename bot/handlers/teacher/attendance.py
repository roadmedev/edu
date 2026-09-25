from aiogram import F, Router
from aiogram.types import CallbackQuery

from api import students as students_api
from api.client import ApiClient, ApiError
from callbacks.attendance import AttendanceCB
from filters.role import RoleFilter
from keyboards.inline.attendance import attendance_kb

router = Router(name="teacher_attendance")
router.callback_query.filter(RoleFilter("teacher"))

# message_id -> {enrollment_id: present}; jarayon bitta xabar doirasida yashaydi
_draft: dict[int, dict[int, bool]] = {}


@router.callback_query(AttendanceCB.filter(F.action == "start"))
async def start_attendance(cb: CallbackQuery, callback_data: AttendanceCB, api: ApiClient):
    data = await students_api.course_students(api, cb.from_user.id, callback_data.course_id)
    if not data["students"]:
        await cb.answer("O'quvchi yo'q.", show_alert=True)
        return

    state = {s["enrollmentId"]: True for s in data["students"]}  # default: hammasi keldi
    msg = await cb.message.answer(
        f"📋 <b>{data['courseTitle']}</b> — bugungi davomat.\nIsm ustiga bosib holatni o'zgartiring:",
        reply_markup=attendance_kb(callback_data.course_id, data["students"], state),
    )
    _draft[msg.message_id] = state
    await cb.answer()


@router.callback_query(AttendanceCB.filter(F.action == "toggle"))
async def toggle_attendance(cb: CallbackQuery, callback_data: AttendanceCB, api: ApiClient):
    state = _draft.setdefault(cb.message.message_id, {})
    state[callback_data.enrollment_id] = not state.get(callback_data.enrollment_id, True)

    data = await students_api.course_students(api, cb.from_user.id, callback_data.course_id)
    await cb.message.edit_reply_markup(reply_markup=attendance_kb(callback_data.course_id, data["students"], state))
    await cb.answer()


@router.callback_query(AttendanceCB.filter(F.action == "save"))
async def save_attendance(cb: CallbackQuery, callback_data: AttendanceCB, api: ApiClient):
    state = _draft.pop(cb.message.message_id, {})
    if not state:
        await cb.answer("Holat topilmadi, qaytadan boshlang.", show_alert=True)
        return

    records = [{"enrollmentId": eid, "present": present} for eid, present in state.items()]
    try:
        result = await students_api.save_attendance(api, cb.from_user.id, callback_data.course_id, records)
    except ApiError as e:
        await cb.answer(e.message, show_alert=True)
        return

    await cb.message.edit_text(f"✅ Davomat saqlandi ({result['date']}, {result['count']} ta o'quvchi).")
    await cb.answer()