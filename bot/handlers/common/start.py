from html import escape

from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove

from keyboards.reply.menu import main_menu
from states.registration import Registration

router = Router(name="common_start")


@router.message(CommandStart())
async def cmd_start(message: Message, user: dict | None, state: FSMContext):
    await state.clear()  # /start har doim jarayonni boshidan boshlaydi

    if user is None:
        await state.set_state(Registration.full_name)
        await message.answer(
            "Assalomu alaykum! O'quv markazimiz botiga xush kelibsiz.\n"
            "Ro'yxatdan o'tish uchun <b>ism va familiyangizni</b> yozing:",
            reply_markup=ReplyKeyboardRemove(),
        )
        return

    await message.answer(
        f"Xush kelibsiz, <b>{escape(user['fullName'])}</b>!",
        reply_markup=main_menu(user["role"]),
    )