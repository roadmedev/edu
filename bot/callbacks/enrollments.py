from aiogram.filters.callback_data import CallbackData


class EnrollCB(CallbackData, prefix="en"):
    action: str  # accept | reject | terms
    enrollment_id: int