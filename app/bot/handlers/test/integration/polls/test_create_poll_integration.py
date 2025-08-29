import pytest
from unittest.mock import AsyncMock, MagicMock, patch, ANY
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import User, Chat, Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from datetime import datetime
from app.bot.handlers.polls.create_poll import (
    create_poll_command,
    capture_title,
    capture_description,
    capture_question,
    capture_answer_type,
    capture_options,
    capture_end,
    PollFSM
)

@pytest.fixture
def fake_user():
    return User(
        id=123,
        is_bot=False,
        first_name="TestUser",
        username="test_user"
    )

@pytest.fixture
def fake_chat():
    return Chat(
        id=123,
        type="private"
    )

@pytest.fixture
def fake_message(fake_user, fake_chat):
    msg = MagicMock(spec=Message)
    msg.message_id = 1
    msg.date = datetime.now()
    msg.chat = fake_chat
    msg.from_user = fake_user
    msg.text = ""
    msg.answer = AsyncMock()
    return msg

@pytest.fixture
def fake_callback(fake_message):
    cb = MagicMock(spec=CallbackQuery)
    cb.id = "test_cb"
    cb.from_user = fake_message.from_user
    cb.chat_instance = "test"
    cb.message = fake_message
    cb.data = ""
    cb.answer = AsyncMock()
    return cb

@pytest.fixture
def db_session():
    session = AsyncMock()
    session.commit = AsyncMock()
    session.add = AsyncMock()
    session.flush = AsyncMock()
    session.get = AsyncMock()
    return session

@pytest.mark.asyncio
async def test_create_poll(fake_message, fake_callback, db_session):
    async def mock_get_db():
        yield db_session
    
    with patch('app.bot.handlers.polls.create_poll.get_db', new=mock_get_db):
        storage = MemoryStorage()
        state = FSMContext(storage, key=fake_message.from_user.id)
        
        mock_poll = MagicMock()
        mock_poll.id = 1
        mock_poll.first_question_id = None
        db_session.get.return_value = mock_poll
        
        mock_question = MagicMock()
        mock_question.id = 1
        db_session.get.return_value = mock_question
        
        await create_poll_command(fake_message, state)
        assert await state.get_state() == PollFSM.title
        fake_message.answer.assert_called_with('Введите название опроса')
        
        fake_message.text = "Мой опрос"
        await capture_title(fake_message, state)
        assert await state.get_state() == PollFSM.description
        fake_message.answer.assert_called_with('Введите описание (- для его отсутствия)')
        
        fake_message.text = "Тестовое описание"
        await capture_description(fake_message, state)
        assert await state.get_state() == PollFSM.question
        fake_message.answer.assert_called_with("Задайте ваш первый вопрос")
        
        fake_message.text = "Какой ваш любимый цвет?"
        await capture_question(fake_message, state)
        assert await state.get_state() == PollFSM.answer_type
        fake_message.answer.assert_called_with(
            "Отлично! Выберите формат ответа.",
            reply_markup=ANY
        )
        
        fake_callback.data = "single_choice"
        await capture_answer_type(fake_callback, state)
        assert await state.get_state() == PollFSM.options
        fake_callback.message.answer.assert_called_with(
            "Введите варианты ответов через тире (-), например:\n"
            "Вариант 1 - Вариант 2 - Вариант 3"
        )

        fake_message.text = "Красный - Синий - Зеленый"
        await capture_options(fake_message, state)
        assert await state.get_state() == PollFSM.question
        fake_message.answer.assert_called_with(
            "Варианты ответов сохранены. \nЗадайте следующий вопрос",
            reply_markup=ANY
        )
        
        fake_callback.data = "end_poll"
        await capture_end(fake_callback, state)
        assert await state.get_state() is None
        fake_callback.message.answer.assert_called_with("Опрос создан", reply_markup=None)
        
        assert db_session.add.call_count >= 2  
        assert db_session.commit.call_count >= 2
