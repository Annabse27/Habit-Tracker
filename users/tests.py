from django.test import TestCase
from users.models import CustomUser
from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token



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
        Проверяет, что суперпользователь создается с флагами is_superuser и is_staff,
        а также корректным паролем.
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
        # Укажите конкретное исключение, если известно
        with self.assertRaises(Exception):
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
        # Проверка на отсутствие telegram_chat_id
        self.assertEqual(user.telegram_chat_id, None)

    def test_invalid_email(self):
        """
        Тест на валидацию email.
        Проверяет, что при попытке создания пользователя с некорректным email
        выбрасывается ошибка ValueError.
        """
        with self.assertRaises(ValueError):
            CustomUser.objects.create_user(
                email="not-an-email",
                password="password123",
                telegram_chat_id="123456789"
            )

    def test_str_representation(self):
        """Тест строкового представления пользователя."""
        user = CustomUser.objects.create_user(
            email="test@example.com",
            password="password123",
            telegram_chat_id="123456789"
        )
        self.assertEqual(str(user), "test@example.com")

    def test_user_permissions(self):
        """Тест на наличие прав доступа у пользователя."""
        user = CustomUser.objects.create_user(
            email="user@example.com",
            password="password123"
        )
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_superuser_permissions(self):
        """Тест на наличие прав доступа у суперпользователя."""
        superuser = CustomUser.objects.create_superuser(
            email="admin@example.com",
            password="password123"
        )
        self.assertTrue(superuser.is_staff)
        self.assertTrue(superuser.is_superuser)

    def test_user_fields(self):
        """Тест на наличие всех полей у пользователя."""
        user = CustomUser.objects.create_user(
            email="user@example.com",
            password="password123",
            phone_number="1234567890",
            telegram_username="user_telegram",
            telegram_chat_id="987654321"
        )
        self.assertEqual(user.email, "user@example.com")
        self.assertEqual(user.phone_number, "1234567890")
        self.assertEqual(user.telegram_username, "user_telegram")
        self.assertEqual(user.telegram_chat_id, "987654321")

    def test_create_superuser_with_invalid_is_staff(self):
        """Проверяет, что нельзя создать суперпользователя без флага is_staff."""
        with self.assertRaises(ValueError):
            CustomUser.objects.create_superuser(
                email="admin@example.com",
                password="password123",
                is_staff=False
            )

    def test_create_superuser_with_invalid_is_superuser(self):
        """Проверяет, что нельзя создать суперпользователя без флага is_superuser."""
        with self.assertRaises(ValueError):
            CustomUser.objects.create_superuser(
                email="admin@example.com",
                password="password123",
                is_superuser=False
            )

    def test_create_user_without_email(self):
        """Тест на валидацию отсутствующего email."""
        with self.assertRaises(ValueError):
            CustomUser.objects.create_user(
                email="",
                password="password123"
            )

    def test_create_user_without_password(self):
        """Тест на валидацию отсутствующего пароля."""
        with self.assertRaises(ValueError):
            CustomUser.objects.create_user(
                email="test@example.com",
                password=""  # Теперь это вызовет ошибку
            )

    def test_telegram_chat_id_is_valid(self):
        """Тест на проверку валидного telegram_chat_id."""
        user = CustomUser.objects.create_user(
            email="test2@example.com",
            password="password123",
            telegram_chat_id="123456789"
        )
        self.assertEqual(user.telegram_chat_id, "123456789")

    def test_telegram_chat_id_is_none(self):
        """Тест на проверку отсутствия telegram_chat_id."""
        user = CustomUser.objects.create_user(
            email="test2@example.com",
            password="password123"
        )
        self.assertIsNone(user.telegram_chat_id)


class UserRegistrationTest(APITestCase):

    def test_user_registration(self):
        url = reverse('user-registration')
        data = {
            'email': 'testuser@example.com',
            'password': 'password123',
            'confirm_password': 'password123'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(CustomUser.objects.count(), 1)
        self.assertEqual(
            CustomUser.objects.get().email,
            'testuser@example.com')


class UserLoginTestCase(APITestCase):

    def setUp(self):
        self.user = CustomUser.objects.create_user(email='testuser@example.com', password='password123')
        self.url = reverse('user-login')

    def test_login_user(self):
        data = {
            'email': 'testuser@example.com',
            'password': 'password123'
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)

    def test_invalid_credentials(self):
        data = {
            'email': 'testuser@example.com',
            'password': 'wrongpassword'
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
