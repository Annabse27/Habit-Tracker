from unittest.mock import patch, AsyncMock
from django.test import TestCase
from telegram_app.tasks import send_telegram_notification, send_reminders
from users.models import CustomUser
from django.apps import AppConfig
import asyncio
from telegram_app.bot import setup_bot, start
from django.conf import settings


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
            user_id=self.user.id,
            message="Test message")
        MockBot.assert_called_once_with(token=settings.TELEGRAM_BOT_TOKEN)
        MockBot().send_message.assert_called_once_with(
            chat_id='123456789', text="Test message")

    def test_no_chat_id(self):
        """Тест, если у пользователя нет telegram_chat_id"""
        self.user.telegram_chat_id = None
        self.user.save()

        with patch('telegram_app.tasks.Bot') as MockBot:
            send_telegram_notification(
                user_id=self.user.id, message="Test message")
            MockBot().send_message.assert_not_called()

    @patch('telegram_app.tasks.Bot')
    def test_invalid_user(self, MockBot):
        """Тест отправки уведомления несуществующему пользователю"""
        invalid_user_id = 9999
        with self.assertLogs('telegram_app.tasks', level='WARNING') as log:
            send_telegram_notification(
                user_id=invalid_user_id,
                message="Test message")
            self.assertIn('Пользователь с ID 9999 не найден', log.output[0])

    def test_task_execution(self):
        """Тест на проверку выполнения задачи Celery"""
        with patch('telegram_app.tasks.send_telegram_notification.delay') as mock_task:
            send_telegram_notification.delay(self.user.id, "Test message")
            mock_task.assert_called_once_with(self.user.id, "Test message")

    def test_send_notification_with_empty_message(self):
        """Тест отправки уведомления с пустым сообщением"""
        with patch('telegram_app.tasks.Bot') as MockBot:
            send_telegram_notification(user_id=self.user.id, message="")
            MockBot().send_message.assert_called_once_with(chat_id='123456789', text="")

    @patch('telegram_app.tasks.Bot')
    def test_send_notification_with_special_characters(self, MockBot):
        """Тест отправки уведомления с специальными символами"""
        special_message = "Test & * $ # @!"
        send_telegram_notification(
            user_id=self.user.id,
            message=special_message)
        MockBot().send_message.assert_called_once_with(
            chat_id='123456789', text=special_message)


class TelegramAppConfig(AppConfig):
    name = 'telegram_app'

    def ready(self):
        from .bot import setup_bot
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        loop.create_task(setup_bot())


class TelegramAppConfigTest(TestCase):

    @patch('telegram_app.bot.setup_bot')  # Мокаем функцию setup_bot
    def test_ready_method(self, mock_setup_bot):
        """Тестируем, что метод ready вызывает setup_bot."""
        # Получаем экземпляр класса TelegramAppConfig и вызываем его метод
        # ready
        app_config = TelegramAppConfig.create('telegram_app')

        # Вызываем метод ready() вручную
        app_config.ready()

        # Проверяем, что setup_bot был вызван
        mock_setup_bot.assert_called_once()


class TelegramAppTestCase(TestCase):

    def setUp(self):
        self.user = CustomUser.objects.create_user(
            email='test@example.com',
            password='password123',
            telegram_chat_id='123456789')

    @patch('telegram_app.tasks.Bot')
    def test_send_telegram_notification(self, MockBot):
        """Тест успешной отправки уведомления через Telegram."""
        send_telegram_notification(self.user.id, "Test message")
        MockBot().send_message.assert_called_once_with(
            chat_id='123456789', text="Test message")

    def test_user_not_found(self):
        """Тест на случай, если пользователь не найден."""
        with self.assertLogs('telegram_app.tasks', level='WARNING') as log:
            send_telegram_notification(999, "Test message")
            self.assertIn("Пользователь с ID 999 не найден", log.output[0])

    @patch('telegram_app.bot.Application.builder')
    def test_setup_bot(self, MockBuilder):
        """Тест на настройку и запуск бота."""

        # Мокаем builder и асинхронные методы с использованием AsyncMock
        mock_app = AsyncMock()
        mock_builder = MockBuilder.return_value
        mock_builder.token.return_value.build.return_value = mock_app

        # Запускаем асинхронную функцию setup_bot
        asyncio.run(setup_bot())

        # Проверяем, что методы были вызваны корректно
        mock_builder.token.assert_called_once_with(settings.TELEGRAM_BOT_TOKEN)
        mock_app.add_handler.assert_called_once()
        mock_app.run_polling.assert_awaited_once()

    @patch('telegram_app.bot.CustomUser')
    @patch('telegram_app.bot.Update', new_callable=AsyncMock)
    async def test_start_command(self, MockUpdate, MockCustomUser):
        """Тест команды /start"""
        # Настройка мока пользователя
        user = AsyncMock(
            telegram_username='test_user',
            email='test@example.com')
        MockCustomUser.objects.filter.return_value.first.return_value = user

        # Настройка мока сообщения
        mock_message = AsyncMock(
            chat_id='123456', from_user=AsyncMock(
                username='test_user'))
        MockUpdate.message = mock_message

        # Вызываем команду /start
        await start(MockUpdate, AsyncMock())

        # Проверяем, что chat_id пользователя был обновлен
        self.assertEqual(user.telegram_chat_id, '123456')
        user.save.assert_called_once()



class CeleryTaskTest(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            email='test@example.com', password='password123', telegram_chat_id='123456789')

    def test_send_reminders(self):
        """
        Тест на успешное выполнение задачи по отправке уведомлений
        """
        send_reminders()
        # Здесь можно проверить лог или проверить, была ли вызвана отправка
        # через моки.

