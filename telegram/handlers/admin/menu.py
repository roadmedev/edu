# handlers/admin/menu.py (to'liq)
from aiogram import Router, F
from aiogram.types import Message

from keyboards.admin_menu import get_admin_menu, get_users_submenu
from utils.filters import IsAdmin

router = Router()
router.message.filter(IsAdmin())
router.callback_query.filter(IsAdmin())


@router.message(F.text == "👥 Foydalanuvchilar")
async def show_users_submenu(message: Message) -> None:
    await message.answer(
        "👥 <b>Foydalanuvchilar bo'limi</b>\n\n"
        "Quyidagi bo'limlardan birini tanlang:",
        parse_mode="HTML",
        reply_markup=get_users_submenu(),
    )


@router.message(F.text == "🔙 Orqaga")
async def back_to_admin_menu(message: Message) -> None:
    await message.answer(
        "🏠 Asosiy menyu:",
        reply_markup=get_admin_menu(),
    )