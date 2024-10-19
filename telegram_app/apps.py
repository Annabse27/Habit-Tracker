import asyncio
from django.apps import AppConfig


class TelegramAppConfig(AppConfig):
    name = 'telegram_app'

    def ready(self):
        from telegram_app.bot import setup_bot  # Импорт setup_bot из bot.py

        # Проверяем наличие event loop и запускаем setup_bot
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        loop.create_task(setup_bot())  # Запуск setup_bot в event loop
