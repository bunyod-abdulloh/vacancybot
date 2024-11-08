from aiogram import Router, types, F

from bot.handlers.functions.functions_one import failed_message

router = Router()


@router.message(F.text == "Ustoz kerak")
async def need_teacher_main(message: types.Message):
    await failed_message(message)
