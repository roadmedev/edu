from aiogram.filters.callback_data import CallbackData


class PayoutCB(CallbackData, prefix="po"):
    action: str  # full | partial
    teacher_id: int