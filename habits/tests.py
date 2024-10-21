from django.test import TestCase, SimpleTestCase
from django.utils import timezone
from habits.models import Habit
from users.models import CustomUser
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from .validators import validate_duration, validate_frequency
from django.core.exceptions import ValidationError
from config import wsgi, asgi
from rest_framework import status

User = get_user_model()

# Тесты для модели Habit и валидаторов

class HabitModelTest(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            email='test@example.com', password='password123')

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

    def test_linked_habit_invalid(self):
        """Тестирование ошибки при указании связанной привычки и вознаграждения одновременно"""
        linked_habit = Habit.objects.create(
            user=self.user,
            action="Полезная привычка",
            time=timezone.now().time(),
            place="Дом",
            frequency=2,
            duration=60,
            is_pleasant=True
        )
        habit = Habit.objects.create(
            user=self.user,
            action="Полезная привычка",
            time=timezone.now().time(),
            place="Дом",
            frequency=2,
            duration=60,
            reward="Кофе",
            linked_habit=linked_habit
        )
        with self.assertRaises(ValidationError):
            habit.clean()

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

    def test_validate_frequency_above_limit(self):
        """Тест для проверки максимальной частоты"""
        with self.assertRaises(ValidationError):
            validate_frequency(8)  # Больше допустимого лимита

