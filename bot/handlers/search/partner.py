from aiogram import Router, F, types

router = Router()


@router.message(F.text == "Sherik kerak")
async def search_partner_rtr(message: types.Message):
    text = ("<b>Sherik topish uchun ariza berish</b>\n\n"
            "Hozir Sizga birnecha savollar beriladi\n"
            "Har biriga javob bering.\n"
            "Oxirida agar hammasi to`g`ri bo`lsa, HA tugmasini bosing va arizangiz Adminga yuboriladi.\n\n")

    await message.answer(
        text=f"{text}Ismingizni kiriting"
    )
