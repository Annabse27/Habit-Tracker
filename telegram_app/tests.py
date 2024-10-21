from unittest.mock import patch, AsyncMock
from django.test import TestCase
from telegram_app.tasks import send_telegram_notification, send_reminders
from users.models import CustomUser
from django.conf import settings
import asyncio


class TelegramNotificationTest(TestCase):

    def setUp(self):
        """Создаем пользователя с указанным chat_id"""
        self.user = CustomUser.objects.create_user(
            email='test@example.com', password='password123')
        self.user.telegram_chat_id = '123456789'
        self.user.save()

    @patch('telegram_app.tasks.Bot')  # Мокаем Telegram Bot для проверки
    def test_send_telegram_notification(self, MockBot):
        """Тест отправки уведомлений через Telegram"""
        send_telegram_notification(
            telegram_chat_id=self.user.telegram_chat_id,
            message="Test message"
        )
        MockBot.assert_called_once_with(token=settings.TELEGRAM_BOT_TOKEN)
        MockBot().send_message.assert_called_once_with(
            chat_id='123456789', text="Test message"
        )

    def test_no_chat_id(self):
        """Тест, если у пользователя нет telegram_chat_id"""
        self.user.telegram_chat_id = None
        self.user.save()

        with patch('telegram_app.tasks.Bot') as MockBot:
            send_telegram_notification(
                telegram_chat_id=self.user.telegram_chat_id, message="Test message"
            )
            MockBot().send_message.assert_not_called()

    @patch('telegram_app.tasks.Bot')
    def test_invalid_user(self, MockBot):
        """Тест отправки уведомления несуществующему пользователю"""
        invalid_telegram_chat_id = '9999'
        with self.assertLogs('telegram_app.tasks', level='ERROR') as log:
            send_telegram_notification(
                telegram_chat_id=invalid_telegram_chat_id,
                message="Test message"
            )
            # Ожидаем ошибку с недействительным telegram_chat_id и текст исключения
            self.assertIn(f"Failed to send message to {invalid_telegram_chat_id}", log.output[0])

    def test_task_execution(self):
        """Тест на проверку выполнения задачи Celery"""
        with patch('telegram_app.tasks.send_telegram_notification.delay') as mock_task:
            send_telegram_notification.delay(self.user.telegram_chat_id, "Test message")
            mock_task.assert_called_once_with(self.user.telegram_chat_id, "Test message")

    def test_send_notification_with_empty_message(self):
        """Тест отправки уведомления с пустым сообщением"""
        with patch('telegram_app.tasks.Bot') as MockBot:
            send_telegram_notification(telegram_chat_id=self.user.telegram_chat_id, message="")
            MockBot().send_message.assert_called_once_with(chat_id='123456789', text="")

    @patch('telegram_app.tasks.Bot')
    def test_send_notification_with_special_characters(self, MockBot):
        """Тест отправки уведомления с специальными символами"""
        special_message = "Test & * $ # @!"
        send_telegram_notification(
            telegram_chat_id=self.user.telegram_chat_id,
            message=special_message
        )
        MockBot().send_message.assert_called_once_with(
            chat_id='123456789', text=special_message
        )


class TelegramAppTestCase(TestCase):

    def setUp(self):
        self.user = CustomUser.objects.create_user(
            email='test@example.com',
            password='password123',
            telegram_chat_id='123456789')

    @patch('telegram_app.tasks.Bot')
    def test_send_telegram_notification(self, MockBot):
        """Тест успешной отправки уведомления через Telegram."""
        send_telegram_notification(self.user.telegram_chat_id, "Test message")
        MockBot().send_message.assert_called_once_with(
            chat_id='123456789', text="Test message"
        )

    def test_user_not_found(self):
        """Тест на случай, если пользователь не найден."""
        with self.assertLogs('telegram_app.tasks', level='WARNING') as log:
            send_telegram_notification('9999', "Test message")
            self.assertIn("Failed to send message to 9999: Chat not found", log.output[0])

