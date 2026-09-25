from aiogram import Router
from aiogram.types import Message

from keyboards.reply.menu import main_menu

router = Router(name="common_fallback")


@router.message()
async def unknown(message: Message, user: dict | None):
    if user is None:
        await message.answer("Ro'yxatdan o'tish uchun /start ni bosing.")
        return
    await message.answer("Quyidagi tugmalardan foydalaning 👇", reply_markup=main_menu(user["role"]))