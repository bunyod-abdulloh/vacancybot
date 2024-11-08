from aiogram import Router, F, types

from bot.handlers.functions.functions_one import failed_message

router = Router()


@router.message(F.text == "Shogird kerak")
async def apprentice_needed_main(message: types.Message):
    await failed_message(message)
