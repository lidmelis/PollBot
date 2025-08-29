from aiogram import Router
from app.bot.handlers import start #, stats
from app.bot.handlers.common import help #, forms
from app.bot.handlers.polls import create_poll, get_polls

def register_handlers(dp):
    main_router = Router()

    main_router.include_router(start.router)
    main_router.include_router(help.router)
    main_router.include_router(create_poll.router)
    main_router.include_router(get_polls.router)

    dp.include_router(main_router)
