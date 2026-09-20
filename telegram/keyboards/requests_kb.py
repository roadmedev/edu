# keyboards/requests_kb.py
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_request_actions_keyboard(request_id: int) -> InlineKeyboardMarkup:
    """So'rov uchun Qabul/Rad tugmalari"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Qabul qilish",
                    callback_data=f"req_accept:{request_id}",
                ),
                InlineKeyboardButton(
                    text="❌ Rad qilish",
                    callback_data=f"req_reject:{request_id}",
                ),
            ]
        ]
    )


def format_request_message(request: dict) -> str:
    """So'rov xabari (teacher'ga keladi)"""
    return (
        f"📨 <b>Yangi kurs so'rovi</b>\n\n"
        f"👤 O'quvchi: <b>{request['full_name']}</b>\n"
        f"📱 Telefon: {request.get('phone_number', '—')}\n"
        f"📚 Kurs: <b>{request['course_title']}</b>\n"
        f"💵 Narx: {request.get('price', 0)} so'm\n"
        f"📅 Sana: {request['created_at'][:16]}\n"
    )