from aiogram import Router, types
from aiogram.types import Message
from aiogram.filters import Command
from sqlalchemy.future import select
from app.core.db import get_db
from app.core.models import Poll
import logging

router = Router()

@router.message(Command("delete_poll"))
async def delete_poll_command(message: Message):
    try:
        args = message.text.split(maxsplit=1)
        if len(args) < 2 or not args[1].isdigit():
            await message.answer("Используйте формат: /delete_poll <ID опроса>")
            return

        poll_id = int(args[1])

        async for db in get_db():
            result = await db.execute(select(Poll).filter(Poll.id == poll_id))
            poll = result.scalar()

            if not poll:
                await message.answer(f"Опрос с ID {poll_id} не найден.")
                return

            db.delete(poll)
            await db.commit()

            await message.answer(f"Опрос с ID {poll_id} удален.")
            logging.info(f"Удален опрос: ID {poll_id}")

    except Exception as e:
        logging.error(f"Ошибка при удалении опроса: {e}")
        await message.answer("Произошла ошибка при удалении опроса.")