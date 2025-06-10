# Переменные
PYTHON = python3
PIP = pip3
VENV = venv
TESTS = tests
REQUIREMENTS = requirements.txt

# Создание виртуального окружения
venvv:
	$(PYTHON) -m venv $(VENV)

# Установка зависимостей
install: venvv
	$(PIP) install -r $(REQUIREMENTS)

# Запуск тестов
test: install
	$(PYTHON) -m pytest $(TESTS)

# Запуск линтера (flake8)
lint: install
	$(PYTHON) -m flake8 $(TESTS)

# Запуск форматтера кода (black)
format: install
	$(PYTHON) -m black $(TESTS)

# Запуск приложения
run: install
	$(PYTHON) main.py

# Очистка проекта
clean:
	rm -rf $(VENV)
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	
# Справка
help:
	@echo "Использование: make [цель]"
	@echo ""
	@echo "Цели:"
	@echo "  install    Установить зависимости"
	@echo "  test       Запустить тесты"
	@echo "  lint       Проверить код с помощью flake8"
	@echo "  format     Отформатировать код с помощью black"
	@echo "  run        Запустить приложение"
	@echo "  clean      Очистить проект"
	@echo "  help       Показать эту справку"

rebuild:
	docker compose down
	docker compose build --no-cache
	docker compose up -d
