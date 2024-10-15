# Используем официальный образ Python
FROM python:3.12-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем pyproject.toml и poetry.lock для установки зависимостей
COPY pyproject.toml poetry.lock /app/

# Устанавливаем Poetry
RUN pip install poetry

# Устанавливаем зависимости без разработки
RUN poetry config virtualenvs.create false \
 && poetry install --no-dev --no-interaction --no-ansi

# Копируем все файлы проекта в контейнер
COPY . .

# Выполняем команды миграции и сбор статических файлов
#CMD ["sh", "-c", "python manage.py migrate && python manage.py collectstatic --noinput && python manage.py runserver 0.0.0.0:8000"]
