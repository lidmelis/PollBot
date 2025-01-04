import logging
from aiogram import Bot, Dispatcher
from app.core.config import load_config
#from app.bot.commands import register_handlers
#from app.core.db import init_db

async def main():
    logging.basicConfig(level=logging.INFO)
    config = load_config()
    print(config.BOT_TOKEN)
    bot = Bot(token=config.BOT_TOKEN)

    dp = Dispatcher()
    
    # Инициализация базы данных
    # await init_db(config.DB_URL)

    # Регистрация хендлеров
    # register_handlers(dp)

    await dp.start_polling(bot)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())