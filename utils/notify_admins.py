import logging

from aiogram import Bot

from data.config import ADMIN_GROUP


async def on_startup_notify(bot: Bot):
    # for admin in ADMINS:
    try:
        bot_properties = await bot.me()
        message = ["<b>Bot ishga tushdi.</b>\n",
                   f"<b>Bot ID:</b> {bot_properties.id}",
                   f"<b>Bot Username:</b> {bot_properties.username}"]
        await bot.send_message(int(ADMIN_GROUP), "\n".join(message))
    except Exception as err:
        logging.exception(err)
