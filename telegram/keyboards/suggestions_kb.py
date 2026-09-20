# keyboards/suggestions_kb.py
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_suggestions_list_keyboard(suggestions: list[dict]) -> InlineKeyboardMarkup:
    """Har bir taklif uchun tugma"""
    buttons = []
    for s in suggestions[:20]:  # Max 20 ta
        # Matnni qisqartiramiz
        short_text = s["message"][:40] + ("..." if len(s["message"]) > 40 else "")
        buttons.append([
            InlineKeyboardButton(
                text=f"#{s['id']} · {s['full_name']} · {short_text}",
                callback_data=f"suggestion:{s['id']}",
            )
        ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_suggestion_actions_keyboard(suggestion_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ O'qildi",
                    callback_data=f"suggestion_mark:{suggestion_id}:read",
                ),
                InlineKeyboardButton(
                    text="🗄 Arxivlash",
                    callback_data=f"suggestion_mark:{suggestion_id}:archived",
                ),
            ],
        ]
    )