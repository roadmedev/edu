from aiogram.filters.callback_data import CallbackData


class MyStudentsCB(CallbackData, prefix="ms"):
    action: str  # course | student | pay | back
    course_id: int
    enrollment_id: int = 0