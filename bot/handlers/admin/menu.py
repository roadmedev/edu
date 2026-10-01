from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from api import admin as admin_api
from api.client import ApiClient
from filters.role import RoleFilter
from keyboards.reply.admin import admin_menu, admin_users_menu
from keyboards.inline.broadcast import broadcast_button
from utils import labels as L
from utils.formatters import format_plain_users

router = Router(name="admin_menu")
router.message.filter(RoleFilter("admin"))


@router.message(F.text == L.USERS)
async def open_users_menu(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("👥 Foydalanuvchilar bo'limi", reply_markup=admin_users_menu())


@router.message(F.text == L.BACK)
async def back_to_admin_menu(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("⬅️ Asosiy menyu", reply_markup=admin_menu())


@router.message(F.text == L.PLAIN_USERS)
async def show_plain_users(message: Message, api: ApiClient):
    rows = await admin_api.plain_users(api, message.from_user.id)
    await message.answer(format_plain_users(rows), reply_markup=broadcast_button("users"))
