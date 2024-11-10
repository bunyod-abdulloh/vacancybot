from aiogram import Router, types, F

from bot.handlers.functions.functions_one import failed_message

router = Router()

text = ["Ism sharifingizni kiriting:", "Yoshingizni kiriting:", "Kerakli texnologiyalarni kiriting:", "Aloqa", "Hudud",
        "Narx tolov qilasizmi", "Ishlaysizmi oqiysizmi", "murojaat vaqti", "maqsad"]


@router.message(F.text == "Ustoz kerak")
async def need_teacher_main(message: types.Message):
    await failed_message(message)
