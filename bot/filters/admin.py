from typing import Union

from aiogram.enums import ChatType
from aiogram.filters import BaseFilter
from aiogram.types import Message, CallbackQuery


class IsBotAdminFilter(BaseFilter):
    def __init__(self, user_ids: list):
        self.user_ids = user_ids

    async def __call__(self, message: Message) -> bool:
        admin_ids_int = [int(id) for id in self.user_ids]
        return int(message.from_user.id) in admin_ids_int


class ChatGroupCallbackFilter(BaseFilter):
    def __init__(self, chat_type: Union[str, list]):
        self.chat_type = chat_type

    async def __call__(self, call: CallbackQuery) -> bool:
        # Faqat `CallbackQuery` uchun `call.message.chat.type` ni tekshiradi
        return call.message and call.message.chat.type == ChatType.SUPERGROUP
