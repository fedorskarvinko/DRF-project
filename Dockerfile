FROM python:3.14-slim

WORKDIR /app

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Установка Poetry
RUN pip install poetry

# Копирование файлов с зависимостями
COPY pyproject.toml poetry.lock* /app/

# Настройка Poetry - НЕ создавать виртуальное окружение
RUN poetry config virtualenvs.create false

# Установка зависимостей (включая Celery)
RUN poetry install --no-interaction --no-ansi --no-root

# Копирование проекта
COPY . .

# Создание всех необходимых директорий
RUN mkdir -p /app/static /app/media /app/logs

# Устанавливаем SECRET_KEY для сборки статики
ENV DEBUG=False
ENV ALLOWED_HOSTS=*

# Cбор статики
RUN SECRET_KEY=temporary-build-key python manage.py collectstatic --noinput

# Настройка переменных окружения
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=config.settings

EXPOSE 8000

CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]