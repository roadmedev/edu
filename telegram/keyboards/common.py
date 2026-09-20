# keyboards/common.py
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_back_button(callback_data: str = "back") -> InlineKeyboardMarkup:
    """🔙 Orqaga tugmasi"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Orqaga", callback_data=callback_data)]
        ]
    )


def get_pagination_keyboard(
    prefix: str,
    page: int,
    total_pages: int,
    extra_buttons: list[list[InlineKeyboardButton]] | None = None,
) -> InlineKeyboardMarkup:
    """Pagination: ←oldingi | 1/5 | keyingi→"""
    buttons = []

    if extra_buttons:
        buttons.extend(extra_buttons)

    nav = []
    if page > 1:
        nav.append(InlineKeyboardButton(text="←", callback_data=f"{prefix}:{page - 1}"))
    nav.append(InlineKeyboardButton(text=f"{page}/{total_pages}", callback_data="noop"))
    if page < total_pages:
        nav.append(InlineKeyboardButton(text="→", callback_data=f"{prefix}:{page + 1}"))

    if nav:
        buttons.append(nav)

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_confirm_keyboard(
    yes_callback: str,
    no_callback: str = "cancel",
    yes_text: str = "✅ Ha",
    no_text: str = "❌ Bekor qilish",
) -> InlineKeyboardMarkup:
    """Tasdiqlash tugmalari"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=yes_text, callback_data=yes_callback),
                InlineKeyboardButton(text=no_text, callback_data=no_callback),
            ]
        ]
    )