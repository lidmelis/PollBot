import asyncio
import logging
from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.chat_action import ChatActionSender
from app.core.db import get_db
from app.core.models import Poll, Question

      
class PollFSM(StatesGroup):
    title = State()
    description = State()
    question = State()
    answer_type = State()


answer_type_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Произвольный ответ"),
            KeyboardButton(text="Одиночный ответ"),
        ],
        [
            KeyboardButton(text="Множественный ответ"),
            KeyboardButton(text="Закончить опрос"),
        ]
    ],
    resize_keyboard=True
)


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
        await state.update_data(poll_id=new_poll.id)
        await message.answer(f"Опрос '{title}' создан! Задайте ваш первый вопрос.")
        logging.info(f"Создан новый опрос: {title}")
    await state.set_state(PollFSM.question)


@router.message(F.text, PollFSM.question)
async def capture_question(message: Message, state: FSMContext):
    if message.text == "Конец":
        await state.clear()
        return 
    
    if len(message.text) > 500:
        await message.answer("Вопрос не должен превышать 500 символов.\nВведите более короткий вопрос")
        return
    
    await state.update_data(question=message.text)
    await message.answer(
        "Отлично! Выберите формат ответа.",
        reply_markup=answer_type_keyboard
    )
    await state.set_state(PollFSM.answer_type)


@router.message(F.text, PollFSM.answer_type)
async def capture_answer_type(message: Message, state: FSMContext):
    with_options = False
    with_multipy_options = False
    match  message.text:
        case "Произвольный ответ":
            pass
        case "Одиночный ответ":
            with_options = True
        case "Множественный ответ":
            with_options = True
            with_multipy_options = True
        case _:
            await message.answer("Формат ответа не совпадает с возможными.\nВыберите другой")
            return
    data = await state.get_data()
    async for db in get_db():
        question = Question(with_options=with_options, with_multipy_options=with_multipy_options, poll_id=data.get("poll_id"), text=data.get("question"))
        db.add(question)
        await db.commit()
        await message.answer(f"Вопрос добален.\nЗадайте следующий.")
        logging.info(f"Добавлен вопрос: {question}")
    await state.set_state(PollFSM.question)

