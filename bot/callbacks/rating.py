from aiogram.filters.callback_data import CallbackData


class RatingCB(CallbackData, prefix="rt"):
    course_id: int