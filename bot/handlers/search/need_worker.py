from aiogram import Router, F, types

from bot.handlers.functions.functions_one import failed_message

router = Router()


@router.message(F.text == "Hodim kerak")
async def need_worker_main(message: types.Message):
    await failed_message(message)
