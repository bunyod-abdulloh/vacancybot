from aiogram import Router, types, F
from aiogram.filters import CommandStart

from bot.keyboards.reply.main_dkb import main_dkb

router = Router()


@router.message(CommandStart())
async def do_start(message: types.Message):
    full_name = message.from_user.full_name
    text = (f"Assalom alaykum {full_name}!\n\nUstozShogird kanalining rasmiy botiga xush kelibsiz!\n\n"
            "/help yordam buyrugi orqali nimalarga qodir ekanligimni bilib oling!")

    await message.answer(
        text=text, reply_markup=main_dkb()
    )


@router.message(F.text == "🏡 Bosh sahifa")
async def back_main_menu(message: types.Message):
    await message.answer(
        text=message.text, reply_markup=main_dkb()
    )
