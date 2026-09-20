# handlers/admin/stats.py
from aiogram import Router, F
from aiogram.types import Message

from services.admin_service import get_center_stats
from utils.filters import IsAdmin

router = Router()
router.message.filter(IsAdmin())


def format_money(amount) -> str:
    """1234567 → 1 234 567"""
    try:
        return f"{int(float(amount)):,}".replace(",", " ")
    except (ValueError, TypeError):
        return str(amount)


@router.message(F.text == "📊 Markaz statistikasi")
async def show_stats(message: Message) -> None:
    stats = await get_center_stats()

    if "error" in stats:
        await message.answer("⚠️ Statistikani yuklashda xatolik yuz berdi.")
        return

    text = (
        f"📊 <b>Markaz statistikasi</b>\n\n"
        f"📚 Fanlar: <b>{stats['subjects']}</b>\n"
        f"👨‍🏫 O'qituvchilar: <b>{stats['teachers']}</b>\n"
        f"👥 Guruhlar: <b>{stats['groups']}</b>\n"
        f"🎓 O'quvchilar: <b>{stats['students']}</b>\n\n"
        f"📅 Bugungi darslar: <b>{stats['today_lessons']}</b>\n"
        f"✅ Bugungi davomat: <b>{stats['today_attendance']}</b>\n\n"
        f"💰 Bu oy to'lovlar: <b>{format_money(stats['month_payments'])} so'm</b>\n"
        f"⚠️ Qarzdorlar: <b>{stats['debtors']} ta</b>"
    )

    await message.answer(text, parse_mode="HTML")