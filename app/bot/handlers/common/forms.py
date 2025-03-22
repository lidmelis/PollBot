from aiogram import Router
from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command  # Добавляем импорт фильтра
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

router = Router()

class FormState(StatesGroup):
    waiting_for_name = State()
    waiting_for_age = State()

# Исправляем декоратор: вместо commands используем фильтр Command
@router.message(Command("form"))
async def form_start(message: Message, state: FSMContext):
    await message.answer("Введите ваше имя:")
    await state.set_state(FormState.waiting_for_name)

@router.message(FormState.waiting_for_name)
async def process_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Введите ваш возраст:")
    await state.set_state(FormState.waiting_for_age)

@router.message(FormState.waiting_for_age)
async def process_age(message: Message, state: FSMContext):
    user_data = await state.get_data()
    name = user_data.get("name")
    age = message.text

    await message.answer(f"Спасибо! Вы ввели:\nИмя: {name}\nВозраст: {age}")
    await state.clear()
