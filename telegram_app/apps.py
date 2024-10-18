import asyncio
from django.apps import AppConfig

class TelegramAppConfig(AppConfig):
    name = 'telegram_app'

    def ready(self):
        from .bot import setup_bot

        # Проверяем, запущен ли событийный цикл
        try:
            loop = asyncio.get_running_loop()  # Получаем текущий event loop, если он уже запущен
        except RuntimeError:  # Если event loop не запущен, создаём новый
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        # Запускаем setup_bot в текущем event loop
        loop.create_task(setup_bot())
