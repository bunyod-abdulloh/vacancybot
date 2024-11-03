from aiogram import Router

from bot.filters import ChatPrivateFilter


def setup_routers() -> Router:
    from bot.handlers.users import start_hr
    from .search import partner
    from .errors import error_handler
    from .admin import check_partner

    router = Router()

    # Agar kerak bo'lsa, o'z filteringizni o'rnating
    start_hr.router.message.filter(ChatPrivateFilter(chat_type=["private"]))
    #  Users
    router.include_routers(start_hr.router, partner.router)
    # Admins
    router.include_routers(check_partner.router)
    return router
