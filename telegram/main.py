import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN

# Handlers
from handlers.start import router as start_router

# Admin
from handlers.admin.menu import router as admin_menu_router
from handlers.admin.stats import router as admin_stats_router
from handlers.admin.users import router as admin_users_router
from handlers.admin.teachers import router as admin_teachers_router
from handlers.admin.students import router as admin_students_router
from handlers.admin.finance import router as admin_finance_router
from handlers.admin.suggestions import router as admin_suggestions_router

# Teacher
from handlers.teacher.menu import router as teacher_menu_router
from handlers.teacher.profile import router as teacher_profile_router
#from handlers.teacher.courses import router as teacher_courses_router
from handlers.teacher.schedules import router as teacher_schedules_router
from handlers.teacher.students import router as teacher_students_router
from handlers.teacher.requests import router as teacher_requests_router
from handlers.teacher.balance import router as teacher_balance_router
from handlers.teacher.suggestions import router as teacher_suggestions_router

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# ⚠️ Tartib muhim!
# 1. Start (eng birinchi)
dp.include_router(start_router)

# 2. Admin (har biri o'z filteriga ega)
dp.include_router(admin_menu_router)
dp.include_router(admin_stats_router)
dp.include_router(admin_users_router)
dp.include_router(admin_teachers_router)
dp.include_router(admin_students_router)
dp.include_router(admin_finance_router)
dp.include_router(admin_suggestions_router)

# 3. Teacher
dp.include_router(teacher_menu_router)
dp.include_router(teacher_profile_router)      # 👤 Mening
#dp.include_router(teacher_courses_router)      # Kurs CRUD
dp.include_router(teacher_schedules_router)    # Dars jadvali
dp.include_router(teacher_students_router)     # 👥 O'quvchilarim
dp.include_router(teacher_requests_router)     # Qabul/Rad
dp.include_router(teacher_balance_router)      # 💰 Balans
dp.include_router(teacher_suggestions_router)  # 💡 Taklif

async def main() -> None:
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())