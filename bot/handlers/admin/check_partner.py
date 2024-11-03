from aiogram import Router, F, types

from loader import bot

router = Router()


@router.callback_query(F.data.startswith('admincheck_yes:'))
async def admincheck_partner(call: types.CallbackQuery):
    user_id = call.data.split(':')[1]
    row_id = call.data.split(':')[2]
    await bot.send_message(
        chat_id=user_id,
        text=f"Sizning <b>Sherik kerak</b> bo'limi uchun yuborgan {user_id}{row_id} raqamli so'rovingiz qabul qilindi!"
    )
    await call.message.edit_text(
        text="Habar foydalanuvchiga yuborildi!"
    )
