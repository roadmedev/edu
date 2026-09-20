# handlers/admin/users.py
from aiogram import Router, F
from aiogram.types import Message

from utils.filters import IsAdmin

router = Router()
router.message.filter(IsAdmin())


@router.message(F.text == "👤 Oddiy foydalanuvchilar")
async def show_regular_users(message: Message) -> None:
    """Oddiy foydalanuvchilar ro'yxati"""
    from services.admin_service import get_students

    users = await get_students(role="user")

    if not users:
        await message.answer("Hozircha oddiy foydalanuvchilar yo'q.")
        return

    lines = [f"👤 <b>{u['full_name']}</b>\n   📱 {u['phone_number']}" for u in users[:50]]
    text = f"<b>Oddiy foydalanuvchilar</b> ({len(users)} ta):\n\n" + "\n\n".join(lines)

    if len(users) > 50:
        text += f"\n\n... va yana {len(users) - 50} ta"

    await message.answer(text, parse_mode="HTML")