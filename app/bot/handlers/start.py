import logging
from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from sqlalchemy.future import select
from app.core.db import get_db
from app.core.models import User

router = Router()

@router.message(Command("start"))
async def start_command(message: Message, state: FSMContext):
    await state.clear() 
    peer_id = message.from_user.id
    await message.answer(str(peer_id))
    try:
        async for db in get_db():
            result = await db.execute(
                select(User).filter(User.peer_id == peer_id)
            )
            existing_user = result.scalar()

            if existing_user:
                return
            new_user = User(peer_id=peer_id)
            db.add(new_user)
            await db.commit()

            logging.info(f"Пользователь с peer_id = {peer_id} был успешно создан!")
        
    except Exception as e:
        logging.error(f"Ошибка при создании пользователя: {e}")
        await message.answer("Произошла ошибка при создании")


    await message.answer(
        "Привет! Я — твой личный помощник для для заполнения форм и сбора статистики!\n"
        "Вот, что я умею:\n"
        "- Создавать и заполнять формы\n"
        "- Обрабатывать ответы и собирать статистику\n"
        "- Помогать в опросах и анкетах\n"
        "Если ты готов, просто введите /forms, и мы начнем!\n"
    )