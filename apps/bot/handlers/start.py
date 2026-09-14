from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove

from states.registration import Registration
from keyboards.contact_kb import get_phone_keyboard
from keyboards.main_menu import get_main_menu
from services.auth_services import register_user, get_user_by_telegram_id

router = Router()

@router.message(CommandStart())
async def start_handler(message: Message, state: FSMContext) -> None:
    
    result = await get_user_by_telegram_id(message.from_user.id)

    if result.get("user"): 
        #Foydalanuvchi allaqachon ro'yxatdan o'tgan
        user = result["user"]
        await message.answer(
            "Asosiy menyu",
            reply_markup=get_main_menu(),
        )
    else:
        #Ro'yxatdan o'tmaganlar uchun
        await state.set_state(Registration.waiting_for_name)
        await message.answer(
            "Assalomu Aleykum! Apex Study telegram bot platformasiga xush kelibsiz 👋" \
            "Botdan to'liq foydalanish uchun avval ro'yxatdan o'tishingizni so'raymiz. \n"
            "Familiya, Ism va Sharifingizni to'liq yozing!"
        )

@router.message(Registration.waiting_for_name)
async def process_name(message: Message, state: FSMContext) -> None:
    await state.update_data(full_name=message.text)
    await state.set_state(Registration.waiting_for_phone)
    await message.answer(
        "Rahmat! Endi telefon raqamingizni yuboring:",
        reply_markup=get_phone_keyboard(),
    )

@router.message(Registration.waiting_for_phone, F.contact)
async def process_phone(message: Message, state: FSMContext) -> None:
    phone_number = message.contact.phone_number
    data = await state.update_data(phone_number=phone_number)
    await state.clear()    

    result = await register_user(
        full_name=data["full_name"],
        phone_number=phone_number,
        telegram_id=message.from_user.id,
    )

    if "error" in result:
        await message.answer(
            "Ro'yxatdan o'tishda xatolik yuz berdi, birozdan so'ng qayta\n" \
            "urinib ko'ring",
            retply_markup=ReplyKeyboardRemove(),
        )
        return

    await message.answer(
        f"Ro'yxatdan o'tish yakunlandi! ✅\n\n"
        f"Ism: {data['full_name']}\n"
        f"Telefon: {phone_number}",
        reply_markup=get_main_menu(),
    )