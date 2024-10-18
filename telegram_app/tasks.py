from celery import shared_task
from telegram import Bot
from django.conf import settings
from users.models import CustomUser
import logging

logger = logging.getLogger(__name__)


@shared_task
def send_telegram_notification(user_id, message):
    try:
        user = CustomUser.objects.get(id=user_id)
        if user.telegram_chat_id:
            bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
            bot.send_message(chat_id=user.telegram_chat_id, text=message)
        else:
            logger.warning(f'У пользователя {user.email} нет telegram_chat_id')
    except CustomUser.DoesNotExist:
        logger.warning(f'Пользователь с ID {user_id} не найден')
