from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def build_list_keyboard(items: list[dict], prefix: str, label_key: str = "name") -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text=item.get(label_key) or item.get("full_name"), callback_data=f"{prefix}:{item['id']}")]
        for item in items
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)