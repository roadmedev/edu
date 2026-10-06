from aiogram.filters.callback_data import CallbackData


class StatsCB(CallbackData, prefix="st"):
    action: str   # months | years | pick_month | pick_year | current
    value: str = ""