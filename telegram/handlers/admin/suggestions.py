# handlers/admin/suggestions.py
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

from services.admin_service import get_suggestions, mark_suggestion
from keyboards.suggestions_kb import (
    get_suggestions_list_keyboard,
    get_suggestion_actions_keyboard,
)
from utils.filters import IsAdmin

router = Router()
router.message.filter(IsAdmin())
router.callback_query.filter(IsAdmin())


@router.message(F.text == "💡 Taklif qutisi")
async def show_suggestions(message: Message) -> None:
    suggestions = await get_suggestions(status="new")

    if not suggestions:
        await message.answer("🎉 Yangi takliflar yo'q.")
        return

    await message.answer(
        f"💡 <b>Yangi takliflar</b> ({len(suggestions)} ta):",
        parse_mode="HTML",
        reply_markup=get_suggestions_list_keyboard(suggestions),
    )


@router.callback_query(F.data.startswith("suggestion:"))
async def show_suggestion_detail(callback: CallbackQuery) -> None:
    suggestion_id = int(callback.data.split(":")[1])

    # Suggestion'ni qayta yuklaymiz
    suggestions = await get_suggestions(status="new")
    suggestion = next((s for s in suggestions if s["id"] == suggestion_id), None)

    if not suggestion:
        await callback.answer("Taklif topilmadi", show_alert=True)
        return

    role_label = {
        "user": "👤 Foydalanuvchi",
        "teacher": "👨‍🏫 O'qituvchi",
    }.get(suggestion["role"], suggestion["role"])

    text = (
        f"💡 <b>Taklif #{suggestion['id']}</b>\n\n"
        f"{role_label}: <b>{suggestion['full_name']}</b>\n"
        f"📱 Telefon: {suggestion.get('phone_number', '—')}\n"
        f"🆔 Telegram: <code>{suggestion['telegram_id']}</code>\n"
        f"📅 Sana: {suggestion['created_at'][:16]}\n\n"
        f"<b>Xabar:</b>\n{suggestion['message']}"
    )

    await callback.message.edit_text(
        text,
        parse_mode="HTML",
        reply_markup=get_suggestion_actions_keyboard(suggestion_id),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("suggestion_mark:"))
async def mark_suggestion_handler(callback: CallbackQuery) -> None:
    _, suggestion_id, status = callback.data.split(":")
    suggestion_id = int(suggestion_id)

    result = await mark_suggestion(suggestion_id, status)

    if "error" in result:
        await callback.answer("Xatolik", show_alert=True)
        return

    label = "✅ O'qildi" if status == "read" else "🗄 Arxivlandi"
    await callback.message.edit_text(
        f"{label} deb belgilandi (Taklif #{suggestion_id})."
    )
    await callback.answer("Saqlandi")