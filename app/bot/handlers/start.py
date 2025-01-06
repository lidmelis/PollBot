from aiogram import Router, types
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

router = Router()

@router.message(commands=["start"])
async def start_command(message: Message, state: FSMContext):
    await state.clear()  # Сброс состояния
    await message.answer(
        "Привет! Я — твой личный помощник для для заполнения форм и сбора статистики!\n"
        "Вот, что я умею:\n"
        "- Создавать и заполнять формы\n"
        "- Обрабатывать ответы и собирать статистику\n"
        "- Помогать в опросах и анкетах\n"
        "Если ты готов, просто введите /forms, и мы начнем!\n"
    )
    