from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from app.core.config import load_config

Base = declarative_base()

# Создание и подключение к базе данных через Alembic
engine = create_async_engine(load_config().DB_URL, echo=True)
SessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

# Создаем таблицы, если они ещё не существуют (только на этапе инициализации)
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# Функция для получения сессии
async def get_db():
    async with SessionLocal() as db:  # Используем async with для работы с сессией
        yield db  # Возвращаем сессию для использования
