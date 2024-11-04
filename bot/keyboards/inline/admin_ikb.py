from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def create_inline_keyboard(buttons):
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def admin_check_ikb(user_id, row_id):
    buttons = [
        [InlineKeyboardButton(text="✅ Tasdiqlash", callback_data=f"admincheck_yes:{user_id}:{row_id}")],
        [InlineKeyboardButton(text="❌ Rad etish", callback_data=f"admincheck_no:{user_id}:{row_id}")]
    ]
    return create_inline_keyboard(buttons)


admin_check_second_ikb = create_inline_keyboard([
    [InlineKeyboardButton(text="✅ Ha", callback_data="admincheck_second_yes")],
    [InlineKeyboardButton(text="❌ Yo'q", callback_data="admincheck_second_no")]
])


def partner_check_ikb(user_id, row_id):
    buttons = [
        [
            InlineKeyboardButton(text="♻️ Yo'q qayta", callback_data=f"admincheck_no:{user_id}:{row_id}"),
            InlineKeyboardButton(text="✅ Ha", callback_data=f"partner_yes:{user_id}")
        ]
    ]
    return create_inline_keyboard(buttons)
