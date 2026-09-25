from aiogram.filters.callback_data import CallbackData


class MyCourseCB(CallbackData, prefix="mc"):
    action: str  # cert | del | delyes | delno
    course_id: int


class DayCB(CallbackData, prefix="day"):
    day: int


class FlowCB(CallbackData, prefix="cf"):
    action: str  # skipcert | addday | save | cancel | timetable | retry