import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN
from handlers.start import router as start_router
from handlers.menu import router as menu_router
from handlers.courses import router as courses_router
from handlers.admin.stats import router as admin_stats_router
from handlers.admin.finance import router as admin_finance_router
from handlers.admin.teachers import router as admin_teachers_router
from handlers.admin.students import router as admin_students_router
from handlers.admin.payments import router as admin_payments_router

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

dp.include_router(start_router)
dp.include_router(menu_router)
dp.include_router(courses_router)
dp.include_router(admin_stats_router)
dp.include_router(admin_finance_router)
dp.include_router(admin_teachers_router)
dp.include_router(admin_students_router)
dp.include_router(admin_payments_router)


async def main() -> None:
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())