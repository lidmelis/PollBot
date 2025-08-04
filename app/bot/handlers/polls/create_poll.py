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
from app.core.models import Poll, Question, AnswerOption
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
    data = await state.get_data()
    logging.debug(f"first_question={data.get('first_question')}")
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
    logging.debug("Entered answer type selection handler")
    
    await callback_query.answer()
    
    # Determine question type from callback
    answer_type = callback_query.data
    with_options = answer_type in ["single_choice", "multipy_choice"]
    with_multipy_options = answer_type == "multipy_choice"
    
    
    if answer_type not in ["arbitrary_choice", "single_choice", "multipy_choice"]:
        logging.warning(f"Invalid answer type received: {answer_type}")
        await callback_query.message.answer("Формат ответа не совпадает с возможными.\nВыберите другой")
        return
    
    async for db in get_db():
        data = await state.get_data()
        
        question = Question(
            with_options=with_options,
            with_multipy_options=with_multipy_options,
            poll_id=data.get("poll_id"),
            text=data.get("question")
        )
        logging.debug(f"Created question object: {question}")
        
        db.add(question)
        await db.flush()  # Get the ID before commit
        
        if data.get("first_question", False):
            poll = await db.get(Poll, data.get("poll_id"))
            if not poll:
                logging.error(f"Poll not found with ID: {data.get('poll_id')}")
                await callback_query.message.answer("Error: Poll not found")
                return
                
            poll.first_question_id = question.id
            await state.update_data({
                "first_question": False,
                "prev_question_id": question.id
            })

        else:
            prev_question_id = data.get("prev_question_id")
            
            if not prev_question_id:
                logging.error("Missing previous question ID in state")
                await callback_query.message.answer("Error: Missing previous question reference")
                return
                
            prev_question = await db.get(Question, prev_question_id)
            if not prev_question:
                logging.error(f"Previous question not found with ID: {prev_question_id}")
                await callback_query.message.answer("Error: Previous question not found")
                return
                
            prev_question.next_question_id = question.id
            question.prev_question_id = prev_question.id
            logging.debug(f"Linked question {question.id} to previous question {prev_question.id}")
        
        await db.commit()
        logging.info(f"Successfully created question with ID: {question.id}")
        
        await state.update_data({
            "prev_question_id": question.id,
            "current_question_id": question.id
        })



    if with_options:
        await callback_query.message.answer(
            "Введите варианты ответов через тире (-), например:\n"
            "Вариант 1 - Вариант 2 - Вариант 3"
        )
        await state.set_state(PollFSM.options)
    else:
        await callback_query.message.answer(
            f"Вопрос добален.\nЗадайте следующий",
            reply_markup=end_keyboard
        )
        await state.set_state(PollFSM.question)

@router.message(F.text, PollFSM.options)
async def capture_options(message: Message, state: FSMContext):
    options = [opt.strip() for opt in message.text.split('-') if opt.strip()]
    if len(options) < 2:
        await message.answer("Нужно ввести хотя бы 2 варианта ответа через тире. Попробуйте еще раз\n"
                           "Например: Вариант 1 - Вариант 2 - Вариант 3")
        return
    async for db in get_db():
        data = await state.get_data()
        question_id = data.get("current_question_id")
        
        for option_text in options:
            db.add(AnswerOption(
                question_id=question_id,
                text=option_text
            ))
        await db.commit()
    await message.answer(
        f"Варианты ответов сохранены. \nЗадайте следующий вопрос",
        reply_markup=end_keyboard
    )
    await state.set_state(PollFSM.question)



@router.callback_query(lambda c: c.data in ["end_poll"])
async def capture_end(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.answer() 
    await callback_query.message.answer(f"Опрос создан", reply_markup=None)
    await state.clear()