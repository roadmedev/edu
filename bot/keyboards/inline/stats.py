from aiogram.types import InlineKeyboardButton as Btn, InlineKeyboardMarkup as Markup

from callbacks.stats import StatsCB


def stats_menu_kb() -> Markup:
    return Markup(inline_keyboard=[
        [
            Btn(text="🗓 Oylar kesimi", callback_data=StatsCB(action="months").pack()),
            Btn(text="📅 Yillar kesimi", callback_data=StatsCB(action="years").pack()),
        ],
        [Btn(text="🔙 Joriy oy", callback_data=StatsCB(action="current").pack())],
    ])


def month_list_kb(periods: list[str]) -> Markup:
    rows = [[Btn(text=p, callback_data=StatsCB(action="pick_month", value=p).pack())] for p in periods]
    rows.append([Btn(text="🔙 Orqaga", callback_data=StatsCB(action="current").pack())])
    return Markup(inline_keyboard=rows)


def year_list_kb(years: list[str]) -> Markup:
    rows = [[Btn(text=y, callback_data=StatsCB(action="pick_year", value=y).pack())] for y in years]
    rows.append([Btn(text="🔙 Orqaga", callback_data=StatsCB(action="current").pack())])
    return Markup(inline_keyboard=rows)