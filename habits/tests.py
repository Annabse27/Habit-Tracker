from django.test import TestCase, SimpleTestCase
from django.utils import timezone
from habits.models import Habit
from users.models import CustomUser
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from habits.tasks import update_next_reminder
from .validators import validate_duration, validate_frequency
from django.core.exceptions import ValidationError
from config import wsgi, asgi


User = get_user_model()

class HabitModelTest(TestCase):
    """
    Тесты для модели Habit
    1. Проверка создания привычки
    2. Проверка строкового представления
    3. Проверка обновления next_reminder
    4. Проверка clean() метода
    """

    def setUp(self):
        self.user = CustomUser.objects.create_user(email='test@example.com', password='password123')

    def test_create_habit(self):
        """Проверяет, что привычка корректно создается в базе данных."""
        habit = Habit.objects.create(
            user=self.user,
            action="Выход на пробежку",
            time=timezone.now().time(),
            place="Парк",
            frequency=2,
            reward="Кофе после пробежки",
            duration=60
        )
        self.assertEqual(habit.action, "Выход на пробежку")
        self.assertEqual(habit.user, self.user)
        self.assertEqual(habit.frequency, 2)

    def test_habit_str_representation(self):
        """Проверяет строковое представление привычки."""
        habit = Habit.objects.create(
            user=self.user,
            action="Выход на пробежку",
            time=timezone.now().time(),
            place="Парк",
            frequency=2,
            reward="Кофе после пробежки",
            duration=60
        )
        self.assertEqual(str(habit), f"Выход на пробежку ({self.user})")

    def test_next_reminder_update(self):
        """Проверяет, что next_reminder обновляется корректно."""
        habit = Habit.objects.create(
            user=self.user,
            action="Выход на пробежку",
            time=timezone.now().time(),
            place="Парк",
            frequency=2,
            reward="Кофе после пробежки",
            duration=60
        )
        initial_reminder = habit.next_reminder
        habit.calculate_next_reminder()
        self.assertNotEqual(habit.next_reminder, initial_reminder)

    def test_habit_clean_method(self):
        """Тестирование логики clean()"""
        habit = Habit.objects.create(
            user=self.user,
            action="Выход на пробежку",
            time=timezone.now().time(),
            place="Парк",
            frequency=2,
            reward="Кофе",
            duration=60
        )
        habit.is_pleasant = True
        habit.reward = "Test Reward"
        with self.assertRaises(ValidationError):
            habit.clean()



class CeleryTaskTest(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(email='test@example.com', password='password123')

    def test_update_next_reminder_task(self):
        """Тест на успешное обновление следующего напоминания с помощью Celery"""
        habit = Habit.objects.create(
            user=self.user,
            action="Выход на пробежку",
            time=timezone.now().time(),
            place="Парк",
            frequency=2,
            reward="Кофе после пробежки",
            duration=60
        )
        update_next_reminder(habit.id)
        habit.refresh_from_db()
        self.assertIsNotNone(habit.next_reminder)

    def test_habit_does_not_exist(self):
        """Тест на случай, когда привычка не существует"""
        non_existing_id = 9999
        with self.assertLogs('habits.tasks', level='INFO') as cm:
            update_next_reminder(non_existing_id)
        self.assertIn('Habit with id 9999 does not exist', cm.output[0])

class HabitValidatorTest(TestCase):
    """
    Тесты для валидаторов
    """

    def test_validate_duration_valid(self):
        """Тест на валидное значение длительности"""
        try:
            validate_duration(100)  # Валидное значение
        except ValidationError:
            self.fail("validate_duration() raised ValidationError unexpectedly!")

    def test_validate_duration_invalid(self):
        """Тест на невалидное значение длительности"""
        with self.assertRaises(ValidationError):
            validate_duration(130)  # Превышает лимит

    def test_validate_frequency_valid(self):
        """Тест на валидную периодичность"""
        try:
            validate_frequency(3)  # Валидное значение
        except ValidationError:
            self.fail("validate_frequency() raised ValidationError unexpectedly!")

    def test_validate_frequency_invalid(self):
        """Тест на невалидную периодичность"""
        with self.assertRaises(ValidationError):
            validate_frequency(0)  # Меньше минимального лимита

class HabitAPITestCase(APITestCase):
    """
    Тесты для CRUD операций через API
    """

    def setUp(self):
        self.user = User.objects.create_user(email='test@example.com', password='password123')
        self.client.force_login(self.user)

    def test_create_habit(self):
        """Тест на создание привычки через API"""
        data = {
            "action": "Прогулка",
            "time": "09:00:00",
            "place": "Парк",
            "is_pleasant": False,
            "frequency": 1,
            "duration": 60,
            "is_public": False,
        }
        response = self.client.post('/api/habits/', data)
        print(response.data)  # Отладочная информация
        self.assertEqual(response.status_code, 201)

    def test_get_habits(self):
        """Тест на получение списка привычек через API"""
        response = self.client.get('/api/habits/')
        self.assertEqual(response.status_code, 200)

    def test_update_habit(self):
        """Тест на обновление привычки через API"""
        habit = Habit.objects.create(
            user=self.user, action="Прогулка", time="09:00:00", place="Парк", frequency=1, duration=60,
            is_pleasant=False
        )
        data = {
            "action": "Пробежка",
            "time": "09:00:00",
            "place": "Парк",
            "is_pleasant": False,
            "frequency": 1,
            "duration": 60,
            "is_public": False,
        }
        response = self.client.put(f'/api/habits/{habit.id}/', data)
        print(response.data)  # Отладочная информация
        self.assertEqual(response.status_code, 200)

    def test_delete_habit(self):
        """Тест на удаление привычки через API"""
        habit = Habit.objects.create(
            user=self.user, action="Прогулка", time="09:00:00", place="Парк", frequency=1, duration=60
        )
        response = self.client.delete(f'/api/habits/{habit.id}/')
        self.assertEqual(response.status_code, 204)


class ASGITestCase(SimpleTestCase):
    def test_asgi_initialization(self):
        self.assertIsNotNone(asgi.application)

class WSGITestCase(SimpleTestCase):
    def test_wsgi_initialization(self):
        self.assertIsNotNone(wsgi.application)

