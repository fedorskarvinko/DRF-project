FROM python:3.13-slim

WORKDIR /app

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Установка Poetry
RUN pip install poetry

# Копирование файлов с зависимостями
COPY pyproject.toml poetry.lock /app/

# Настройка Poetry - НЕ создавать виртуальное окружение
RUN poetry config virtualenvs.create false

# Установка зависимостей (включая Celery)
RUN poetry install --no-interaction --no-ansi --no-root

# Добавляем PATH для бинарников Poetry
ENV PATH="/root/.local/bin:${PATH}"

# Копирование остального проекта
COPY . .

# Создание директорий для статики и медиа
RUN mkdir -p /app/static /app/media

# Настройка переменных окружения
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=config.settings

# Открываем порт
EXPOSE 8000

# Запуск приложения
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]