import logging
from aiogram import Bot, Dispatcher
from app.core.config import load_config
from app.bot.commands import register_handlers

async def main():
    config = load_config()
    logging.basicConfig(level=config.LOG_LEVEL)
    logging.debug(config.BOT_TOKEN)
    bot = Bot(token=config.BOT_TOKEN)

    dp = Dispatcher()
    
    # Инициализация базы данных
    # await init_db(config.DB_URL)

    # Регистрация хендлеров
    register_handlers(dp)

    await dp.start_polling(bot)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
    