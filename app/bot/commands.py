from aiogram import Router
from app.bot.handlers import start, help, forms #, stats

def register_handlers(dp):
    main_router = Router()

    main_router.include_router(start.router)
    main_router.include_router(help.router)
    main_router.include_router(forms.router)

    dp.include_router(main_router)
