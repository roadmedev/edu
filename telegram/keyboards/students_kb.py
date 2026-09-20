# keyboards/students_kb.py
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def build_list_keyboard(
    items: list[dict],
    prefix: str,
    label_key: str = "name",
) -> InlineKeyboardMarkup:
    """
    Umumiy ro'yxat klaviaturasi.

    Args:
        items: dict'lar ro'yxati (har birida 'id' va label_key bo'lishi shart)
        prefix: callback_data prefiksi (masalan: "stu_subject")
        label_key: tugma matni uchun kalit ("name" yoki "full_name")

    Returns:
        InlineKeyboardMarkup
    """
    buttons = []
    for item in items:
        # Label: avval label_key, keyin full_name, keyin "N/A"
        label = item.get(label_key) or item.get("full_name") or f"#{item['id']}"
        buttons.append([
            InlineKeyboardButton(
                text=label,
                callback_data=f"{prefix}:{item['id']}",
            )
        ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)