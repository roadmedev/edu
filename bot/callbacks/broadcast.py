from aiogram.filters.callback_data import CallbackData

class BroadcastCB(CallbackData, prefix="bc"):
    action: str             # start | confirm | cancel
    target: str = ""        # users | teachers | students (faqat "start"da kerak)