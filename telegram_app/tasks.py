from telegram import Bot
from django.conf import settings
from celery import shared_task
import logging
import asyncio

logger = logging.getLogger(__name__)

# Асинхронная функция для отправки сообщений
async def async_send_telegram_notification(telegram_chat_id, message):
    logger.info(f"Attempting to send message to {telegram_chat_id}")
    bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
    try:
        await bot.send_message(chat_id=telegram_chat_id, text=message)
        logger.info(f"Message sent successfully to {telegram_chat_id}")
    except Exception as e:
        logger.error(f"Failed to send message to {telegram_chat_id}: {str(e)}")

# Синхронная Celery задача, которая вызывает асинхронную функцию через asyncio.run()
@shared_task
def send_telegram_notification(telegram_chat_id, message):
    asyncio.run(async_send_telegram_notification(telegram_chat_id, message))

# Синхронная Celery задача для отправки напоминаний
@shared_task
def send_reminders():
    from users.models import CustomUser
    users = CustomUser.objects.filter(telegram_chat_id__isnull=False)
    logger.info("Task send_reminders has started.")
    # Ваша логика отправки напоминаний
    logger.info("Task send_reminders has finished.")

    logger.info(f"Found {len(users)} users to send reminders to.")
    for user in users:
        message = "Не забудьте выполнить свою привычку!"
        logger.info(f"Preparing to send reminder to user: {user.email}, telegram_chat_id: {user.telegram_chat_id}")
        send_telegram_notification(telegram_chat_id=user.telegram_chat_id, message=message)
    logger.info("All reminders have been processed.")
