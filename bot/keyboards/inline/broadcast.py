from aiogram.types import InlineKeyboardButton as Btn, InlineKeyboardMarkup as Markup

from callbacks.broadcast import BroadcastCB
from utils import labels as L

def broadcast_button(target: str) -> Markup:
    return Markup(inline_keyboard=[[
        Btn(text=L.BROADCAST, callback_data=BroadcastCB(action="start", target=target).pack())
    ]])

def broadcast_confirm_kb() -> Markup:
    return Markup(inline_keyboard=[
        [Btn(text="✅ Yuborishni tasdiqlash", callback_data=BroadcastCB(action="confirm").pack())],
        [
            Btn(text="✏️ Tahrirlash", callback_data=BroadcastCB(action="edit").pack()),
            Btn(text="❌ Bekor qilish", callback_data=BroadcastCB(action="cancel").pack()),
        ]
    ])