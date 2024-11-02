from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

check_dkb = ReplyKeyboardMarkup(
    keyboard=[[
        KeyboardButton(
            text="♻️ Qayta kiritish"
        ),
        KeyboardButton(
            text="✅ Tasdiqlash"
        )
    ]],
    resize_keyboard=True
)
