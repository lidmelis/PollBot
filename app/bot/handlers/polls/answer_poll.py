from aiogram import Router, types
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import Command
from sqlalchemy.future import select
from app.core.db import get_db
from app.core.models import Poll, Question
import logging

router = Router()

class AnswerFSM(StatesGroup):
    answer = State()
    
@router.message(Command("answer_poll"))
async def answer_poll_command(message: Message, state: FSMContext):
    await state.clear()
    args = message.text.split(maxsplit=1)
    if len(args) < 2 or not args[1].isdigit():
        await message.answer("Используйте формат: /answer_poll <ID опроса>")
        return

    poll_id = int(args[1])

    logging.debug(f"poll_id from user message = {poll_id}")

    async for db in get_db():
        result = await db.execute(
            select(Poll).filter(Poll.id == message.poll_id)
        )
        poll = result.scalar_one_or_none()

        if poll is None:
            await message.answer("Такого опроса не существует. Извинитесь.")
            return
    
        first_question_id = poll.first_question_id

        logging.debug(f"first question id(from poll #{poll_id}) = {first_question_id}")

        await state.update_data(current_question_id=first_question_id)



    

