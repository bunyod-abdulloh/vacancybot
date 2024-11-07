from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def create_inline_keyboard(button_data):
    buttons = [[InlineKeyboardButton(text=text, callback_data=data)] for text, data in button_data]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def first_check_ikb(telegram_id, row_id, department=None):
    return create_inline_keyboard([
        ("✅ Tasdiqlash", f"admincheck_yes:{telegram_id}:{row_id}:{department}"),
        ("❌ Rad etish", f"admincheck_no:{telegram_id}:{row_id}:{department}")
    ])

admin_check_second_ikb = create_inline_keyboard([
    ("✅ Ha", "admincheck_second_yes"),
    ("❌ Yo'q", "admincheck_second_no")
])


def second_check_ikb(user_id, row_id, department):
    return create_inline_keyboard([
        ("♻️ Yo'q qayta", f"admincheck_no:{user_id}:{row_id}:{department}"),
        ("✅ Ha", f"partner_yes:{user_id}:{department}")
    ])
