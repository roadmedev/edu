import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from api.client import ApiClient
from config import settings
from handlers.common import start, registration, fallback
from handlers.user import courses as user_courses, terms as user_terms
from handlers.teacher import attendance as teacher_attendance, my_courses, course_create, requests as teacher_requests, balance as teacher_balance, students as teacher_students, suggest as teacher_suggest
from handlers.student import my as student_my, schedule as student_schedule, rating as student_rating
from handlers.common import help as common_help
from handlers.admin import (
    stats as admin_stats, menu as admin_menu, teacher as admin_teachers,
    students as admin_students, finance as admin_finance, suggestions as admin_suggestions,
)

from middlewares.auth import AuthMiddleware


async def main():
    logging.basicConfig(level=logging.INFO)

    api = ApiClient(settings.api_url, settings.api_key)
    bot = Bot(settings.bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    # api har bir handler va middleware'ga `api` nomi bilan uzatiladi
    dp = Dispatcher(api=api)
    dp.update.outer_middleware(AuthMiddleware())
    #----------------user--------------------#
    dp.include_router(start.router)
    dp.include_router(registration.router)
    dp.include_router(user_courses.router)
    
    dp.include_router(my_courses.router)
    dp.include_router(course_create.router)
    dp.include_router(teacher_requests.router)
    dp.include_router(teacher_students.router)
    dp.include_router(teacher_attendance.router)
    dp.include_router(teacher_balance.router)
    dp.include_router(teacher_suggest.router)
    dp.include_router(user_terms.router)
    #--------O'quvchiga aylangan bo'lsa ------#
    dp.include_router(student_my.router)
    dp.include_router(student_schedule.router)
    dp.include_router(student_rating.router)
    dp.include_router(common_help.router)
    #-------Admin uchun amallar--------------#
    dp.include_router(admin_stats.router)
    dp.include_router(admin_menu.router)
    dp.include_router(admin_teachers.router)
    dp.include_router(admin_students.router)
    dp.include_router(admin_finance.router)
    dp.include_router(admin_suggestions.router)
    #---------------------------------------#
    dp.include_router(fallback.router)


    try:
        await dp.start_polling(bot)
    finally:
        await api.close()
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())