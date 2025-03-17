from aiogram import Router, types
from aiogram.types import Message
from aiogram.filters import Command
from sqlalchemy.future import select
from app.core.db import get_db
from app.core.models import Poll
import logging

router = Router()

@router.message(Command("create_poll"))
async def create_poll_command(message: Message):
    try:
        args = message.text.split(maxsplit=1)
        if len(args) < 2:
            await message.answer("Используйте формат: /create_poll <название опроса>")
            return

        poll_name = args[1]

        async for db in get_db():
            new_poll = Poll(name=poll_name)
            db.add(new_poll)
            await db.commit()

            await message.answer(f"Опрос '{poll_name}' создан! ID опроса: {new_poll.id}")
            logging.info(f"Создан новый опрос: {poll_name}")

    except Exception as e:
        logging.error(f"Ошибка при создании опроса: {e}")
        await message.answer("Произошла ошибка при создании опроса.")