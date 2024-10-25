from aiogram.types import KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder

buttons_text = ["Sherik kerak", "Ish joyi kerak", "Hodim kerak", "Ustoz kerak", "Shogird kerak"]


def main_dkb():
    button = ReplyKeyboardBuilder()
    for text in buttons_text:
        button.add(KeyboardButton(text=text))
    button.adjust(2)
    return button.as_markup(resize_keyboard=True)
