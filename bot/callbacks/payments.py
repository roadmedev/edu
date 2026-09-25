from aiogram.filters.callback_data import CallbackData


class PayCB(CallbackData, prefix="pay"):
    action: str  # full | partial
    enrollment_id: int