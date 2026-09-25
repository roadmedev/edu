from aiogram.filters.callback_data import CallbackData


class JoinCB(CallbackData, prefix="join"):
    course_id: int