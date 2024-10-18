import logging
from telegram import Update
from telegram.ext import Application, CommandHandler
from django.conf import settings
from users.models import CustomUser

# Логирование
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Функция для команды /start
async def start(update: Update, context):
    chat_id = update.message.chat_id
    telegram_username = update.message.from_user.username

    # Сохраняем chat_id
    user = CustomUser.objects.filter(telegram_username=telegram_username).first()  # Найдите пользователя по Telegram username
    if user:
        user.telegram_chat_id = chat_id
        user.save()
        await update.message.reply_text(f"Привет, {user.email}! Ваш Telegram-чат ID сохранен.")
    else:
        await update.message.reply_text("Пользователь с таким Telegram username не найден.")


# Настройка бота
async def setup_bot():
    # Получаем токен бота из настроек
    token = settings.TELEGRAM_BOT_TOKEN

    # Настраиваем приложение бота
    application = Application.builder().token(token).build()

    # Обработчик для команды /start
    application.add_handler(CommandHandler("start", start))

    # Запуск polling (запрос обновлений) с использованием метода run_polling()
    await application.run_polling()
