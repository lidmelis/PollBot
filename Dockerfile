# Используем базовый образ Python
FROM python:3.12-slim

# Устанавливаем рабочую директорию
WORKDIR /pollbot

# Копируем зависимости
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код приложения
COPY . .

# Команда запуска Alembic для применения миграций
# RUN alembic upgrade head

# Указываем команду для запуска бота
CMD ["python", "main.py"]

