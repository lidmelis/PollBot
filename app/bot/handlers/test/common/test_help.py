import pytest
from unittest.mock import AsyncMock
from app.bot.handlers.common.help import help_command

@pytest.mark.asyncio
async def test_help_command():
    # Создаём фейковое сообщение
    message = AsyncMock()
    message.text = "/help"

    await help_command(message)

    message.answer.assert_awaited()
    actual_text = message.answer.await_args[0][0]
    assert actual_text == (
        "Я здесь, чтобы сделать вашу работу с формами максимально легкой и удобной.\n"
        "Вот несколько команд, которые ты можешь использовать:\n"
        "1️⃣ /start - Начать работу с ботом\n"
        "2️⃣ /forms - Начать создание своей формы или анкеты.\n"
        "3️⃣ /help - помощь\n"
        "4️⃣ /stats - посмотреть статистику"   
    )
