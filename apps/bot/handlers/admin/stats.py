from aiogram import Router, F
from aiogram.types import Message

from services.admin_service import get_center_stats

router = Router()


@router.message(F.text == "📊 Markaz statistikasi")
async def show_stats(message: Message) -> None:
    stats = await get_center_stats()

    if "error" in stats:
        await message.answer("Statistikani yuklashda xatolik yuz berdi.")
        return

    text = (
        f"📊 <b>Markaz statistikasi</b>\n\n"
        f"Fanlar — {stats['subjects']}\n"
        f"O'qituvchilar — {stats['teachers']}\n"
        f"Guruhlar — {stats['groups']}\n"
        f"O'quvchilar — {stats['students']}\n\n"
        f"Bugungi darslar — {stats['today_lessons']}\n"
        f"Bugungi davomat — {stats['today_attendance']}\n\n"
        f"Bu oy to'lovlar — {stats['month_payments']} so'm\n"
        f"Qarzdorlar — {stats['debtors']} ta"
    )

    await message.answer(text, parse_mode="HTML")