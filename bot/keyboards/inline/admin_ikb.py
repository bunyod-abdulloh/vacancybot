from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def create_inline_keyboard(button_data):
    buttons = [[InlineKeyboardButton(text=text, callback_data=data)] for text, data in button_data]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def admin_check_ikb(user_id, row_id):
    return create_inline_keyboard([
        ("✅ Tasdiqlash", f"admincheck_yes:{user_id}:{row_id}"),
        ("❌ Rad etish", f"admincheck_no:{user_id}:{row_id}")
    ])

admin_check_second_ikb = create_inline_keyboard([
    ("✅ Ha", "admincheck_second_yes"),
    ("❌ Yo'q", "admincheck_second_no")
])

def partner_check_ikb(user_id, row_id):
    return create_inline_keyboard([
        ("♻️ Yo'q qayta", f"admincheck_no:{user_id}:{row_id}"),
        ("✅ Ha", f"partner_yes:{user_id}")
    ])
