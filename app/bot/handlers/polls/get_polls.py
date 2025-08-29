import logging
from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from sqlalchemy.future import select
from app.core.db import get_db
from app.core.models import Poll

router = Router()

@router.message(Command("get_polls"))
async def get_polls(message: Message, state: FSMContext):
    try:
        async for db in get_db():
            result = await db.execute(
                select(Poll).filter(Poll.peer_id == message.from_user.id)
            )
            user_polls = result.scalars().all() 

            logging.info(f"User polls: {user_polls}")

            if user_polls:
                msg = "Ваши опросы:\n" + "\n".join(poll.title for poll in user_polls)
            else:
                msg = "У вас пока нет опросов."

            await message.answer(msg)

    except Exception as e:
        logging.error(f"Error fetching polls: {e}")
        await message.answer("Произошла ошибка при получении опросов.")

    finally:
        await state.clear()
