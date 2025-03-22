import asyncio
import logging
import re
from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
#from aiogram.dispatcher import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message
from aiogram.utils.chat_action import ChatActionSender
from app.core.db import get_db
from app.core.models import Poll

      
class PollFSM(StatesGroup):
    title = State()
    description = State()
    

router = Router()

@router.message(Command("create_poll"))
async def create_poll_command(message: Message, state: FSMContext):
    await state.clear()
    async with ChatActionSender.typing(bot=message.bot, chat_id=message.chat.id):
        await asyncio.sleep(2)
        await message.answer('Введите название опроса')
    await state.set_state(PollFSM.title)


@router.message(F.text, PollFSM.title)
async def capture_title(message: Message, state: FSMContext):
    if len(message.text) > 150:
        await message.answer('Длина названия не должна превышать 150 символов.\nВведите более короткое название')
        return
    await state.update_data(title=message.text)
    async with ChatActionSender.typing(bot=message.bot, chat_id=message.chat.id):
        await asyncio.sleep(2)
        await message.answer('Введите описание (- для его отсутствия)')
    await state.set_state(PollFSM.description)

    
@router.message(F.text, PollFSM.description)
async def capture_description(message: Message, state: FSMContext):
    if len(message.text) > 300:
        await message.answer('Описание не должно превышать 300 символов.\nВведите более короткое описание')
        return
    await state.update_data(description=message.text)
    data = await state.get_data()
    title = data.get("title")
    description = data.get("description")
    async for db in get_db():
        new_poll = Poll(title=title, description=description, peer_id=message.from_user.id)
        db.add(new_poll)
        await db.commit()
        await message.answer(f"Опрос '{title}' создан! ID опроса: {new_poll.id}")
        logging.info(f"Создан новый опрос: {title}")
    await state.clear()
