from pydantic_settings import BaseSettings
from pydantic import Field


class Config(BaseSettings):
    BOT_TOKEN: str = Field(..., env="BOT_TOKEN")  # Токен Telegram-бота
    DB_URL: str = Field(..., env="DB_URL")        # URL для подключения к базе данных
    LOG_LEVEL: str = Field("INFO", env="LOG_LEVEL")  # Уровень логирования

    class Config:
        env_file = ".env"  # Указываем, что настройки загружаются из .env файла
        env_file_encoding = "utf-8"

def load_config() -> Config:
    return Config()
