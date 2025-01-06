from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

router = Router()

@router.message(Command("help"))
async def help_command(message: Message):
    await message.answer(
        "Я здесь, чтобы сделать вашу работу с формами максимально легкой и удобной.\n"
        "Вот несколько команд, которые ты можешь использовать:\n"
        "1️⃣ /start - Начать работу с ботом\n"
        "2️⃣ /forms - Начать создание своей формы или анкеты.\n"
        "3️⃣ /help - помощь\n"
        "4️⃣ /stats - посмотреть статистику"   
    )