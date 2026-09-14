from aiogram import Router, F
from aiogram.types import Message

router = Router()

@router.message(F.text == "📈 Mening progressim")
async def show_progress(message: Message) -> None:
    await message.answer("Tez kunda ...")

@router.message(F.text == "ℹ️ Yordam")
async def show_help(message: Message) -> None:
    await message.answer(
        "Edu Platform bot yordamchisi.\n\n"
        "/start — botni qayta ishga tushirish\n"
        "📚 Kurslar — mavjud kurslarni ko'rish\n"
        "📈 Mening progressim — o'zlashtirishingizni kuzatish"
    )