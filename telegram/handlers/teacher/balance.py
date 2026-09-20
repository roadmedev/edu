# handlers/teacher/balance.py
from aiogram import Router, F
from aiogram.types import Message

from services.teacher_service import get_balance
from utils.filters import IsTeacher

router = Router()
router.message.filter(IsTeacher())


def format_money(amount) -> str:
    try:
        return f"{int(float(amount)):,}".replace(",", " ")
    except (ValueError, TypeError):
        return str(amount)


@router.message(F.text == "💰 Balans")
async def show_balance(message: Message) -> None:
    result = await get_balance(message.from_user.id)

    if "error" in result:
        await message.answer("⚠️ Balansni yuklashda xatolik.")
        return

    current = result.get("current_month", {})
    total = result.get("total", {})
    history = result.get("monthly_history", [])

    text = (
        f"💰 <b>Balans</b>\n\n"
        f"<b>Joriy oy:</b>\n"
        f"💵 Umumiy daromad: {format_money(current.get('gross_income', 0))} so'm\n"
        f"🏦 Markaz ulushi (30%): {format_money(current.get('admin_share', 0))} so'm\n"
        f"✅ Sizga: <b>{format_money(current.get('teacher_share', 0))} so'm</b>\n\n"
        f"<b>Jami (barcha vaqt):</b>\n"
        f"💵 Umumiy: {format_money(total.get('total_gross', 0))} so'm\n"
        f"✅ Sizga: <b>{format_money(total.get('total_earned', 0))} so'm</b>"
    )

    if history:
        text += "\n\n<b>📅 Oxirgi oylar:</b>\n"
        for h in history[:6]:
            month = h["month"][:7]
            share = format_money(h["teacher_share"])
            text += f"  • {month}: <b>{share} so'm</b>\n"

    await message.answer(text, parse_mode="HTML")