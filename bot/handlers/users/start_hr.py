from aiogram import Router, types, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext

from bot.keyboards.reply.main_dkb import main_dkb

router = Router()


@router.message(CommandStart())
async def do_start(message: types.Message, state: FSMContext):
    await state.clear()
    text = ("Ish e'loni joylash uchun Mukammal Telegram Bot"
            "\n\nPostlar yuboriladigan kanal:\n"
            "https://t.me/muhibsamplechannel"
            "\n\n<b>Botning mavjud imkoniyatlari:</b>\n\n"
            "- kanalga postlarni tegishli hashtaglar ostida joylash;\n\n"
            "- foydalanuvchi postda xatolikka yo'l qo'ygan bo'lsa habar berish;\n\n"
            "- foydalanuvchidan e'lon qabul qilish va tekshirib tasdiqlash (tasdiq tugmasida bosilganidan keyin habar "
            "tegishli kanalga yuboriladi)\n\n"
            "<b>Qo'shilishi mumkin bo'lgan imkoniyatlar:</b>\n\n"
            "- to'lov tizimini ulash;\n\n"
            "- postlarni foydalanuvchi to'lov qilganidan keyin kanalga joylash;\n\n"
            "- admin panel;\n\n"
            "- foydalanuvchilar statistikasi;\n\n"
            "- foydalanuvchilarga habar yuborish;\n\n"
            "- postlar statistikasi (soha va bo'limlar bo'yicha)\n\n"
            "- vakant band qilingan bo'lsa habarni kanaldan o'chirish;\n\n"
            "- e'lon joylash bo'limlarini kategoriyalarga ko'ra filtrlash (yosh, soha, hudud bo'yicha);\n\n"
            "- guruh/kanallaringiz sohalarga ajratilgan bo'lsa, har biriga alohida-alohida postlarni yuborish;\n\n"
            "- va boshqa ko'plab Siz xohlagan imkoniyatlarni qo'shishimiz mumkin. (Agar dasturiy tomondan imkoni bo'lsa)")

    await message.answer(
        text=text, reply_markup=main_dkb()
    )

@router.message(F.text == "🏡 Bosh sahifa")
async def back_main_menu(message: types.Message):
    await message.answer(
        text=message.text, reply_markup=main_dkb()
    )
