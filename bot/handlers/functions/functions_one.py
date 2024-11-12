import traceback

from aiogram.enums import ChatMemberStatus

from bot.keyboards.inline.admin_ikb import first_check_ikb
from data.config import ADMINS
from loader import bot


async def check_channel_subscription(user_id: int, channel_id: int) -> bool:
    member = await bot.get_chat_member(chat_id=channel_id, user_id=user_id)
    if member.status == ChatMemberStatus.MEMBER or str(member.user.id) in ADMINS:
        return True
    else:
        return False


def extracter(all_medias, delimiter):
    empty_list = []
    for e in range(0, len(all_medias), delimiter):
        empty_list.append(all_medias[e:e + delimiter])
    return empty_list


async def failed_message(message, err):
    tb = traceback.format_tb(err.__traceback__)
    trace = tb[0]
    bot_properties = await bot.me()
    bot_message = f"Bot: {bot_properties.full_name}"

    await message.answer(text=f"{bot_message}\n\nXatolik:\n{trace}\n\n{err}")


async def warning_message(message):
    await message.answer(
        text="Faqat <b>✅ Tasdiqlash</b> yoki <b>♻️ Qayta kiritish</b> buyruqlari kiritilishi lozim!")


async def send_to_admin(chapter, row_id, telegram_id, summary, department):
    await bot.send_message(
        chat_id=ADMINS[0], text=f"{chapter} bo'limiga yangi habar qabul qilindi!\n\n{summary}",
        reply_markup=first_check_ikb(telegram_id=telegram_id, row_id=row_id, department=department)
    )
