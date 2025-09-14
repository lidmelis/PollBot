from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram import types
from sqlalchemy.future import select
from app.core.db import get_db
from app.core.models import Question, AnswerOption


choose_options_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Произвольный ответ", callback_data="arbitrary_choice")
        ],
        [   
            InlineKeyboardButton(text="Одиночный ответ", callback_data="single_choice")
        ],
        [   
            InlineKeyboardButton(text="Множественный ответ",callback_data="multipy_choice")
        ]
    ]
)


end_keyboard = InlineKeyboardMarkup(
    inline_keyboard = [
        [
            InlineKeyboardButton(text="Закончить опрос", callback_data="end_poll")
        ]
    ]
)



async def create_question_keyboard(question_id: int):
    async for db in get_db():
        result = await db.execute(
            select(AnswerOption.id, AnswerOption.text).filter(AnswerOption.question_id == question_id)
        )
        options = result.all()
        
        keyboard = types.InlineKeyboardMarkup(inline_keyboard=[])
        for option_id, option_text in options:
            keyboard.inline_keyboard.append([
                types.InlineKeyboardButton(
                    text=option_text,
                    callback_data=f"answer_{question_id}_{option_id}"
                )
            ])
        
        result = await db.execute(
            select(Question.with_multipy_options).filter(Question.id == question_id)
        )
        with_multipy_options = result.scalar_one_or_none()
        
        if with_multipy_options:
            keyboard.inline_keyboard.append([
                types.InlineKeyboardButton(
                    text="Закончить выбор.",
                    callback_data=f"finish_{question_id}"
                )
            ])
        
        return keyboard

async def get_question_info(question_id: int):
    async for db in get_db():
        result = await db.execute(
            select(
                Question.id, 
                Question.text, 
                Question.next_question_id, 
                Question.with_options, 
                Question.with_multipy_options
            ).filter(Question.id == question_id)
        )
        return result.one_or_none()