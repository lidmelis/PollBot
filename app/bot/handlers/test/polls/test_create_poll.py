import pytest
from unittest.mock import MagicMock, AsyncMock, patch, ANY
from aiogram.fsm.context import FSMContext
from types import SimpleNamespace
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

@pytest.mark.asyncio
async def test_create_poll_command():
    message = AsyncMock()
    state = MagicMock(spec=FSMContext)
    state.set_state = AsyncMock()
    await create_poll_command(message, state)
    message.answer.assert_awaited_with('Введите название опроса')
    state.set_state.assert_awaited_with(PollFSM.title)

@pytest.mark.asyncio
async def test_capture_title_valid():
    message = AsyncMock(text="Valid Title")
    state = AsyncMock()
    await capture_title(message, state)
    state.update_data.assert_awaited_with(title="Valid Title")
    message.answer.assert_awaited_with('Введите описание (- для его отсутствия)')
    state.set_state.assert_awaited_with(PollFSM.description)

@pytest.mark.asyncio
async def test_capture_title_too_long():
    message = AsyncMock(text="A" * 151)
    state = AsyncMock()
    await capture_title(message, state)
    message.answer.assert_awaited_with(
        'Длина названия не должна превышать 150 символов.\nВведите более короткое название'
    )
    state.update_data.assert_not_called()


@pytest.mark.asyncio
@patch("app.bot.handlers.polls.create_poll.get_db")
async def test_capture_description_valid(mock_get_db):
    message = AsyncMock()
    message.text = "Test Description"
    message.answer = AsyncMock()
    message.from_user = SimpleNamespace(id=777)

    state = AsyncMock(spec=FSMContext)
    state.get_data = AsyncMock(side_effect=[{"title": "Test Title"}, {"first_question": True}])

    mock_db = SimpleNamespace(
        add=MagicMock(),
        commit=AsyncMock(),
    )

    async def mock_get_db_gen():
        yield mock_db
    mock_get_db.side_effect = mock_get_db_gen

    await capture_description(message, state)

    state.update_data.assert_any_await(description="Test Description")
    message.answer.assert_awaited_once_with("Задайте ваш первый вопрос")
    state.set_state.assert_awaited_once_with(PollFSM.question)

    mock_db.add.assert_called_once()
    mock_db.commit.assert_awaited_once()


@pytest.mark.asyncio
@patch("app.bot.handlers.polls.create_poll.get_db")
async def test_capture_description_long(mock_get_db):
    message = AsyncMock()
    message.text = "A" * 550
    message.answer = AsyncMock()
    message.from_user = SimpleNamespace(id=777)

    state = AsyncMock(spec=FSMContext)
    state.get_data = AsyncMock(side_effect=[{"title": "Test Title"}, {"first_question": True}])

    mock_db = SimpleNamespace(
        add=MagicMock(),
        commit=AsyncMock(),
    )

    async def mock_get_db_gen():
        yield mock_db
    mock_get_db.side_effect = mock_get_db_gen

    await capture_description(message, state)

    state.update_data.assert_not_called()
    message.answer.assert_awaited_once_with("Описание не должно превышать 300 символов.\nВведите более короткое описание")
    state.set_state.assert_not_called()

    mock_db.add.assert_not_called()
    mock_db.commit.assert_not_called()

@pytest.mark.asyncio
async def test_capture_question_valid():
    message = AsyncMock(text="Test Question?")
    state = AsyncMock()
    await capture_question(message, state)
    state.update_data.assert_awaited_with(question="Test Question?")
    message.answer.assert_awaited_with(
        "Отлично! Выберите формат ответа.",
        reply_markup=ANY
    )
    state.set_state.assert_awaited_with(PollFSM.answer_type)

@pytest.mark.asyncio
@patch('app.bot.handlers.polls.create_poll.get_db')
async def test_capture_answer_type_single_choice(mock_get_db):
    callback = AsyncMock()
    callback.data = "single_choice"
    callback.message = AsyncMock()
    state = AsyncMock()
    mock_db = AsyncMock()
    mock_get_db.return_value = mock_db
    await capture_answer_type(callback, state)
    callback.answer.assert_awaited()
    callback.message.answer.assert_awaited_with(
        "Введите варианты ответов через тире (-), например:\n"
        "Вариант 1 - Вариант 2 - Вариант 3"
    )
    state.set_state.assert_awaited_with(PollFSM.options)


@pytest.mark.asyncio
@patch('app.bot.handlers.polls.create_poll.get_db')
async def test_capture_options_valid(mock_get_db):
    message = AsyncMock(text="Option 1 - Option 2 - Option 3")
    state = AsyncMock()
    state.get_data.return_value = {"current_question_id": 1}
    
    mock_db = AsyncMock()
    mock_db.add = AsyncMock()
    mock_db.commit = AsyncMock()
    
    async def mock_get_db_gen():
        yield mock_db
    
    mock_get_db.return_value = mock_get_db_gen()
    
    await capture_options(message, state)
    
    assert mock_db.add.call_count == 3
    mock_db.commit.assert_awaited_once()
    message.answer.assert_awaited_with(
        "Варианты ответов сохранены. \nЗадайте следующий вопрос",
        reply_markup=ANY
    )
    state.set_state.assert_awaited_with(PollFSM.question)


@pytest.mark.asyncio
async def test_capture_end():
    callback = AsyncMock()
    callback.message = AsyncMock()
    state = AsyncMock()
    await capture_end(callback, state)
    callback.answer.assert_awaited()
    callback.message.answer.assert_awaited_with("Опрос создан", reply_markup=None)
    state.clear.assert_awaited()