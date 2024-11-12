from aiogram import Router

from bot.filters import ChatPrivateFilter


def setup_routers() -> Router:
    from bot.handlers.users import start_hr
    from .search import need_partner, need_job, need_apprentice, need_worker, need_teacher
    from .errors import error_handler
    from .admin import check

    router = Router()

    # Agar kerak bo'lsa, o'z filteringizni o'rnating
    start_hr.router.message.filter(ChatPrivateFilter(chat_type=["private"]))

    #  Users
    router.include_routers(start_hr.router, need_partner.router, need_job.router, need_apprentice.router,
                           need_worker.router, need_teacher.router)
    # Admins
    router.include_routers(check.router)
    return router
