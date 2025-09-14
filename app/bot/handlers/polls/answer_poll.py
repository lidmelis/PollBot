from aiogram import F, Router, types
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import Command
from sqlalchemy.future import select
from app.core.db import get_db
from app.core.models import Poll, Question, AnswerOption
from app.bot.keyboards import create_question_keyboard, get_question_info
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
            select(Poll.first_question_id).filter(Poll.id == poll_id)
        )
        first_question_id = result.scalar_one_or_none()

        if first_question_id is None:
            await message.answer("Такого опроса не существует. Извинитесь.")
            return
        
        question_info = await get_question_info(first_question_id)
        if question_info is None:
            await message.answer("Опрос пустой. Извинитесь.")
            return
        
        id, text, next_question_id, with_options, with_multipy_options = question_info
        
        if with_options:
            keyboard = await create_question_keyboard(id)
            await message.answer(text, reply_markup=keyboard)
        else:
            await message.answer(text)
            await state.update_data(current_question_id=id, text=text, next_question_id=next_question_id)
            await state.set_state(AnswerFSM.answer)


@router.callback_query(F.data.startswith("answer_"))
async def handle_button_answer(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    
    data_parts = callback.data.split('_')
    question_id = int(data_parts[1])
    option_id = int(data_parts[2])
    
    user_id = callback.from_user.id
    logging.info(f"user(ID={user_id}) press answer_option_{option_id} button")
    
    async for db in get_db():
        result = await db.execute(
            select(Question.with_multipy_options, Question.next_question_id)
            .filter(Question.id == question_id)
        )
        question_info = result.one_or_none()
        
        if not question_info:
            await callback.message.answer("Вопрос не найден. Извинитесь.")
            return
            
        with_multipy_options, next_question_id = question_info
        
        if not with_multipy_options:
            logging.info(f"User selected option {option_id} for question {question_id}")
            
            if next_question_id:
                await process_next_question(callback.message, next_question_id, state)
            else:
                await callback.message.answer("Опрос окончен.")
                await state.clear()


@router.callback_query(F.data.startswith("finish_"))
async def handle_finish_multiple_choice(callback: CallbackQuery, state: FSMContext):
    await callback.answer("Ответы приняты.")
    
    question_id = int(callback.data.split('_')[1])
    
    user_id = callback.from_user.id
    logging.info(f"user(ID={user_id}) press finish button")
    
    async for db in get_db():
        result = await db.execute(
            select(Question.next_question_id).filter(Question.id == question_id)
        )
        next_question_id = result.scalar_one_or_none()
        
        if next_question_id:
            await process_next_question(callback.message, next_question_id, state)
        else:
            await callback.message.answer("Опрос окончен.")
            await state.clear()


async def process_next_question(message: Message, next_question_id: int, state: FSMContext):

    question_info = await get_question_info(next_question_id)

    if question_info is None:
        await message.answer("Следующий вопрос не найден. Опрос завершен.")
        await state.clear()
        return
    
    id, text, next_id, with_options, with_multipy_options = question_info
    
    if with_options:
        keyboard = await create_question_keyboard(id)
        await message.answer(text, reply_markup=keyboard)
    else:
        await message.answer(text)
        await state.update_data(current_question_id=id, text=text, next_question_id=next_id)
        await state.set_state(AnswerFSM.answer)
        

@router.message(F.text, AnswerFSM.answer)
async def capture_answer(message: Message, state: FSMContext):
    data = await state.get_data()
    current_question_id = data.get("current_question_id")

    logging.debug(f"User's answer on question {current_question_id} is {message.text}")

    async for db in get_db():
        result = await db.execute(
            select(Question).filter(Question.id == current_question_id)
        )
        current_question = result.scalar_one_or_none()
        
        if current_question is None:
            await message.answer("Такого опроса не существует. Извинитесь.")
            await state.clear()
            return

        next_question_id = current_question.next_question_id
        
        if next_question_id is None:
            await message.answer("Опрос окончен.")
            await state.clear()
            return
        
        next_question_info = await get_question_info(next_question_id)
        
        if next_question_info is None:
            await message.answer("Следующий вопрос не существует. Извинитесь.")
            await state.clear()
            return

        id, text, next_id, with_options, with_multipy_options = next_question_info
        
        if with_options:
            keyboard = await create_question_keyboard(next_question_id)
            await message.answer(text, reply_markup=keyboard)
        else:
            await message.answer(text)
            await state.update_data(current_question_id=next_question_id, next_question_id=next_id)