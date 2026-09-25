from aiogram import F, Router
from aiogram.types import Message

from keyboards.inline.help import help_kb
from utils import labels as L
from utils.texts import HELP_TEXT

router = Router(name="common_help")


@router.message(F.text == L.HELP)
async def help_section(message: Message, user: dict | None):
    if user is None:
        return
    await message.answer(HELP_TEXT, reply_markup=help_kb())