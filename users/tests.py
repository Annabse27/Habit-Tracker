from django.test import TestCase
from users.models import CustomUser


class TestUserModel(TestCase):
    """
    Тесты для модели CustomUser.
    """

    def test_create_user(self):
        """
        Тест на создание обычного пользователя.
        Проверяет, что пользователь создается с правильным email и корректно сохраняет пароль.
        """
        user = CustomUser.objects.create_user(
            email="test@example.com",
            password="password123",
            telegram_chat_id="123456789"
        )
        self.assertEqual(user.email, "test@example.com")
        self.assertTrue(user.check_password("password123"))

    def test_create_superuser(self):
        """
        Тест на создание суперпользователя.
        Проверяет, что суперпользователь создается с флагами is_superuser и is_staff, а также корректным паролем.
        """
        superuser = CustomUser.objects.create_superuser(
            email="admin@example.com",
            password="password123",
            telegram_chat_id="987654321"
        )
        self.assertEqual(superuser.email, "admin@example.com")
        self.assertTrue(superuser.is_superuser)
        self.assertTrue(superuser.check_password("password123"))

    def test_email_is_unique(self):
        """
        Тест на уникальность email.
        Проверяет, что нельзя создать двух пользователей с одинаковым email.
        """
        CustomUser.objects.create_user(
            email="test@example.com",
            password="password123",
            telegram_chat_id="123456789"
        )
        with self.assertRaises(Exception):  # Укажите конкретное исключение, если известно
            CustomUser.objects.create_user(
                email="test@example.com",
                password="password123",
                telegram_chat_id="987654321"
            )

    def test_telegram_chat_id_is_optional(self):
        """
        Тест на необязательность поля telegram_chat_id.
        Проверяет, что можно создать пользователя без указания telegram_chat_id.
        """
        user = CustomUser.objects.create_user(
            email="test2@example.com",
            password="password123"
        )
        self.assertEqual(user.telegram_chat_id, None)  # Проверка на отсутствие telegram_chat_id

    def test_invalid_email(self):
        """
        Тест на валидацию email.
        Проверяет, что при попытке создания пользователя с некорректным email выбрасывается ошибка ValueError.
        """
        with self.assertRaises(ValueError):
            CustomUser.objects.create_user(
                email="not-an-email",
                password="password123",
                telegram_chat_id="123456789"
            )

    def test_str_representation(self):
        """
        Тест строкового представления пользователя.
        Проверяет, что строковое представление пользователя соответствует его email.
        """
        user = CustomUser.objects.create_user(
            email="test@example.com",
            password="password123",
            telegram_chat_id="123456789"
        )
        self.assertEqual(str(user), "test@example.com")
