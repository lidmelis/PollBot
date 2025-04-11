import asyncio
import logging
from aiogram import F, Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message
from aiogram.utils.chat_action import ChatActionSender
from sqlalchemy.future import select
from app.core.db import get_db
from app.core.models import Poll, Question
from app.bot.keyboards import choose_options_keyboard, end_keyboard

      
class PollFSM(StatesGroup):
    title = State()
    description = State()
    question = State()
    answer_type = State()
    options = State()

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
        await state.update_data(first_question=True)
        await message.answer(f"Задайте ваш первый вопрос")
        logging.info(f"Создан новый опрос: {title}")
    await state.set_state(PollFSM.question)


@router.message(F.text, PollFSM.question)
async def capture_question(message: Message, state: FSMContext):
    if len(message.text) > 500:
        await message.answer("Вопрос не должен превышать 500 символов.\nВведите более короткий вопрос")
        return
    
    await state.update_data(question=message.text)
    await message.answer(
        "Отлично! Выберите формат ответа.",
        reply_markup=choose_options_keyboard
    )
    await state.set_state(PollFSM.answer_type)


@router.callback_query(lambda c: c.data in ["arbitrary_choice", "single_choice", "multipy_choice"])
async def capture_answer_type(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.answer() 
    with_options = False
    with_multipy_options = False
    match callback_query.data:
        case "arbitrary_choice":
            pass
        case "single_choice":
            with_options = True
        case "multipy_choice":
            with_options = True
            with_multipy_options = True
        case _:
            await callback_query.message.answer("Формат ответа не совпадает с возможными.\nВыберите другой")
            return
    data = await state.get_data()
    async for db in get_db():
        question = Question(with_options=with_options, with_multipy_options=with_multipy_options, poll_id=data.get("poll_id"), text=data.get("question"))
        if data.get("first_question") == True:
            '''poll = db.query(Poll).filter(
                Poll.id == data.get("poll_id")
                ).first()'''
            
            result = await db.execute(
                select(Poll).filter(Poll.id == data.get("poll_id"))
                )
            poll = result.scalars().first()


            poll.first_question_id = question.id
            await state.update_data(first_question=False)
            await state.update_data(prev_question_id = question.id)

        else:
            '''prev_question = db.query(Question).filter(
                Question.poll_id == data.get("poll_id"),
                Question.next_question_id == None
            ).order_by(Question.id.desc()).first()'''

            result = await db.execute(
                select(Question).filter(
                    Question.poll_id == data.get("poll_id"),
                    Question.next_question_id == None
                    ).order_by(Question.id.desc())
                )
            prev_question = result.scalars().first()


        db.add(question)
        await db.commit()
        await callback_query.message.answer(
            f"Вопрос добален.\nЗадайте следующий",
            reply_markup=end_keyboard
        )
        logging.info(f"Добавлен вопрос: {question}")
    await state.set_state(PollFSM.question)


@router.callback_query(lambda c: c.data in ["end_poll"])
async def capture_end(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.answer() 
    await callback_query.message.answer(f"Опрос создан", reply_markup=None)
    await state.clear()

