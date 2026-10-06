from aiogram import F, Router
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


@router.message(F.text == L.STATS)
async def show_stats(message: Message, api: ApiClient):
    data = await admin_api.stats(api, message.from_user.id)
    await message.answer(format_stats(data), reply_markup=stats_menu_kb())


@router.callback_query(StatsCB.filter(F.action == "current"))
async def show_current(cb: CallbackQuery, api: ApiClient):
    data = await admin_api.stats(api, cb.from_user.id)
    await cb.message.edit_text(format_stats(data), reply_markup=stats_menu_kb())
    await cb.answer()


@router.callback_query(StatsCB.filter(F.action == "months"))
async def show_months(cb: CallbackQuery, api: ApiClient):
    periods = await admin_api.stats_periods(api, cb.from_user.id)
    if not periods["periods"]:
        await cb.answer("Hozircha ma'lumot yo'q.", show_alert=True)
        return
    await cb.message.edit_text("🗓 Qaysi oy bo'yicha ma'lumot kerak?", reply_markup=month_list_kb(periods["periods"]))
    await cb.answer()


@router.callback_query(StatsCB.filter(F.action == "years"))
async def show_years(cb: CallbackQuery, api: ApiClient):
    periods = await admin_api.stats_periods(api, cb.from_user.id)
    if not periods["years"]:
        await cb.answer("Hozircha ma'lumot yo'q.", show_alert=True)
        return
    await cb.message.edit_text("📅 Qaysi yil bo'yicha ma'lumot kerak?", reply_markup=year_list_kb(periods["years"]))
    await cb.answer()


@router.callback_query(StatsCB.filter(F.action == "pick_month"))
async def pick_month(cb: CallbackQuery, callback_data: StatsCB, api: ApiClient):
    data = await admin_api.stats(api, cb.from_user.id, period=callback_data.value)
    await cb.message.edit_text(format_stats(data), reply_markup=stats_menu_kb())
    await cb.answer()


@router.callback_query(StatsCB.filter(F.action == "pick_year"))
async def pick_year(cb: CallbackQuery, callback_data: StatsCB, api: ApiClient):
    data = await admin_api.stats(api, cb.from_user.id, year=callback_data.value)
    await cb.message.edit_text(format_stats(data), reply_markup=stats_menu_kb())
    await cb.answer()