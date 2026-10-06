from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import CallbackQuery, Message

from api import admin as admin_api
from api.client import ApiClient
from callbacks.stats import StatsCB
from filters.role import RoleFilter
from keyboards.inline.stats import month_list_kb, stats_menu_kb, year_list_kb
from utils import labels as L
from utils.formatters import format_stats

router = Router(name="admin_stats")
router.message.filter(RoleFilter("admin"))
router.callback_query.filter(RoleFilter("admin"))


async def _safe_edit(cb: CallbackQuery, text: str, reply_markup):
    """Matn/tugma avvalgisi bilan aynan bir xil bo'lsa, Telegram xato beradi — buni jim o'tkazib yuboramiz."""
    try:
        await cb.message.edit_text(text, reply_markup=reply_markup)
    except TelegramBadRequest as e:
        if "message is not modified" not in str(e):
            raise


@router.message(F.text == L.STATS)
async def show_stats(message: Message, api: ApiClient):
    data = await admin_api.stats(api, message.from_user.id)
    await message.answer(format_stats(data), reply_markup=stats_menu_kb())


@router.callback_query(StatsCB.filter(F.action == "current"))
async def show_current(cb: CallbackQuery, api: ApiClient):
    data = await admin_api.stats(api, cb.from_user.id)
    await _safe_edit(cb, format_stats(data), stats_menu_kb())
    await cb.answer()


@router.callback_query(StatsCB.filter(F.action == "months"))
async def show_months(cb: CallbackQuery, api: ApiClient):
    periods = await admin_api.stats_periods(api, cb.from_user.id)
    if not periods["periods"]:
        await cb.answer("Hozircha ma'lumot yo'q.", show_alert=True)
        return
    await _safe_edit(cb, "🗓 Qaysi oy bo'yicha ma'lumot kerak?", month_list_kb(periods["periods"]))
    await cb.answer()


@router.callback_query(StatsCB.filter(F.action == "years"))
async def show_years(cb: CallbackQuery, api: ApiClient):
    periods = await admin_api.stats_periods(api, cb.from_user.id)
    if not periods["years"]:
        await cb.answer("Hozircha ma'lumot yo'q.", show_alert=True)
        return
    await _safe_edit(cb, "📅 Qaysi yil bo'yicha ma'lumot kerak?", year_list_kb(periods["years"]))
    await cb.answer()


@router.callback_query(StatsCB.filter(F.action == "pick_month"))
async def pick_month(cb: CallbackQuery, callback_data: StatsCB, api: ApiClient):
    data = await admin_api.stats(api, cb.from_user.id, period=callback_data.value)
    await _safe_edit(cb, format_stats(data), stats_menu_kb())
    await cb.answer()


@router.callback_query(StatsCB.filter(F.action == "pick_year"))
async def pick_year(cb: CallbackQuery, callback_data: StatsCB, api: ApiClient):
    data = await admin_api.stats(api, cb.from_user.id, year=callback_data.value)
    await _safe_edit(cb, format_stats(data), stats_menu_kb())
    await cb.answer()