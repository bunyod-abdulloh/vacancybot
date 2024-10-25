from aiogram import Router

from bot.filters import ChatPrivateFilter


def setup_routers() -> Router:
    from .uz import (id_hr)
    from bot.handlers.users import start_hr
    from .search import partner
    from .errors import error_handler
    from .admin import admin_main, admin_users, admin_downloads, admin_check

    router = Router()

    # Agar kerak bo'lsa, o'z filteringizni o'rnating
    start_hr.router.message.filter(ChatPrivateFilter(chat_type=["private"]))
    #  Users
    router.include_routers(start_hr.router, id_hr.router, partner.router)
    # Admins
    router.include_routers(admin_main.router, admin_users.router, admin_downloads.router, admin_check.router)
    return router
