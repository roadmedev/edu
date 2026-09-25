from aiogram.filters.callback_data import CallbackData


class AttendanceCB(CallbackData, prefix="att"):
    action: str  # start | toggle | save
    course_id: int
    enrollment_id: int = 0