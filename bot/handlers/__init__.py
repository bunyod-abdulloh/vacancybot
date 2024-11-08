from aiogram import Router

from bot.filters import ChatPrivateFilter, ChatGroupCallbackFilter


def setup_routers() -> Router:
    from bot.handlers.users import start_hr
    from .search import partner, job, apprentice, need_worker, need_teacher
    from .errors import error_handler
    from .admin import check

    router = Router()

    # Agar kerak bo'lsa, o'z filteringizni o'rnating
    start_hr.router.message.filter(ChatPrivateFilter(chat_type=["private"]))
    check.router.message.filter(ChatPrivateFilter(chat_type=["supergroup"]))
    check.router.callback_query.filter(ChatGroupCallbackFilter(chat_type=["supergroup"]))

    #  Users
    router.include_routers(start_hr.router, partner.router, job.router, apprentice.router, need_worker.router,
                           need_teacher.router)
    # Admins
    router.include_routers(check.router)
    return router
