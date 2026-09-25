from html import escape

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from api import users as users_api
from api.client import ApiClient, ApiError
from keyboards.reply.common import phone_keyboard
from keyboards.reply.menu import main_menu
from states.registration import Registration

router = Router(name="common_registration")


@router.message(Registration.full_name, F.text)
async def get_full_name(message: Message, state: FSMContext):
    name = " ".join(message.text.split())  # ortiqcha bo'shliqlarni tozalaydi

    if not 3 <= len(name) <= 100 or any(ch.isdigit() for ch in name):
        await message.answer("Iltimos, ism va familiyangizni harflar bilan to'g'ri yozing:")
        return

    await state.update_data(full_name=name)
    await state.set_state(Registration.phone)
    await message.answer(
        "Endi pastdagi tugma orqali telefon raqamingizni yuboring:",
        reply_markup=phone_keyboard(),
    )


@router.message(Registration.full_name)
async def full_name_invalid(message: Message):
    await message.answer("Iltimos, ism va familiyangizni matn ko'rinishida yozing:")


@router.message(Registration.phone, F.contact)
async def get_phone(message: Message, state: FSMContext, api: ApiClient):
    contact = message.contact

    # Boshqa odamning kontaktini yuborib qo'ymasligi uchun
    if contact.user_id != message.from_user.id:
        await message.answer("Iltimos, faqat o'zingizning raqamingizni yuboring (tugma orqali).")
        return

    data = await state.get_data()
    try:
        user = await users_api.register(
            api, message.from_user.id, data["full_name"], contact.phone_number
        )
    except ApiError as e:
        if e.status == 409:  # allaqachon bor ekan, shuni ishlatamiz
            user = await users_api.get_by_telegram_id(api, message.from_user.id)
        else:
            await message.answer("Ro'yxatdan o'tishda xatolik. Keyinroq /start bosib qayta urinib ko'ring.")
            return

    await state.clear()
    await message.answer(
        f"✅ Ro'yxatdan o'tdingiz, <b>{escape(user['fullName'])}</b>!",
        reply_markup=main_menu(user["role"]),
    )


@router.message(Registration.phone)
async def phone_invalid(message: Message):
    await message.answer("Raqamni yozib emas, pastdagi «📱 Raqamni yuborish» tugmasi orqali yuboring.")