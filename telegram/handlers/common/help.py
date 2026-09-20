# handlers/common/help.py
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

router = Router()


HELP_TEXT = (
    "ℹ️ <b>Yordam</b>\n\n"
    "<b>Buyruqlar:</b>\n"
    "/start — Botni qayta ishga tushirish\n\n"
    "<b>Bo'limlar:</b>\n"
    "📚 Kurslar — mavjud kurslar ro'yxati\n"
    "📖 Mening — sizning kurslaringiz va so'rovlaringiz\n"
    "📅 Dars jadvali — umumiy dars jadvali\n"
    "⭐ Reyting — o'zlashtirish reytingingiz\n\n"
    "Savol yoki taklif bo'lsa — admin bilan bog'laning."
)


def get_help_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📩 Adminga yozish", callback_data="contact_admin")]
        ]
    )


@router.message(F.text == "ℹ️ Yordam")
async def show_help(message: Message) -> None:
    await message.answer(HELP_TEXT, parse_mode="HTML", reply_markup=get_help_keyboard())


@router.callback_query(F.data == "contact_admin")
async def contact_admin(callback: CallbackQuery) -> None:
    await callback.message.answer(
        "Taklifingizni yuborish uchun 💡 Taklif tugmasidan foydalaning.\n"
        "Yoki admin bilan bog'lanish uchun: @admin_username"
    )
    await callback.answer()