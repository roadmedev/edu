from aiogram.types import InlineKeyboardButton as Btn, InlineKeyboardMarkup as Markup

from callbacks.rating import RatingCB


def course_pick_kb(items: list[dict]) -> Markup:
    rows = [[Btn(text=it["courseTitle"], callback_data=RatingCB(course_id=it["courseId"]).pack())]
            for it in items]
    return Markup(inline_keyboard=rows)