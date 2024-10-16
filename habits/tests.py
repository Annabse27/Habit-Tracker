"""
1. **`test_create_habit`**: Проверяет, что привычка корректно создается в базе данных.
2. **`test_next_reminder_update`**: Проверяет, что при вызове функции
обновления `next_reminder` дата обновляется корректно.
3. **`test_habit_str_representation`**: Проверяет корректность строкового
представления привычки.
4. **`test_update_next_reminder_task`**: Тестирует работу Celery задачи
`update_next_reminder`, чтобы убедиться, что она корректно обновляет
поле `next_reminder`.
"""
from django.test import TestCase
from django.utils import timezone
from habits.models import Habit
from users.models import CustomUser
class HabitModelTest(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(email='test@example.com', password='password123')
    def test_create_habit(self):
        habit = Habit.objects.create(
            user=self.user,
            action="Выход на пробежку",
            time=timezone.now().time(),
            place="Парк",
            frequency=2,  # Исправлено с 'period' на 'frequency'
            reward="Кофе после пробежки",
            duration=60
        )
        self.assertEqual(habit.action, "Выход на пробежку")
        self.assertEqual(habit.user, self.user)
        self.assertEqual(habit.frequency, 2)  # Исправлено
    def test_habit_str_representation(self):
        habit = Habit.objects.create(
            user=self.user,
            action="Выход на пробежку",
            time=timezone.now().time(),
            place="Парк",
            frequency=2,  # Исправлено с 'period' на 'frequency'
            reward="Кофе после пробежки",
            duration=60
        )
        self.assertEqual(str(habit), f"Выход на пробежку ({self.user})")
    def test_next_reminder_update(self):
        habit = Habit.objects.create(
            user=self.user,
            action="Выход на пробежку",
            time=timezone.now().time(),
            place="Парк",
            frequency=2,  # Исправлено с 'period' на 'frequency'
            reward="Кофе после пробежки",
            duration=60
        )
        initial_reminder = habit.next_reminder
        habit.calculate_next_reminder()
        self.assertNotEqual(habit.next_reminder, initial_reminder)
class CeleryTaskTest(TestCase):
    def setUp(self):
        # Создаем пользователя для тестов
        self.user = CustomUser.objects.create_user(email='test@example.com', password='password123')

    def test_update_next_reminder_task(self):
        habit = Habit.objects.create(
            user=self.user,
            action="Выход на пробежку",
            time=timezone.now().time(),
            place="Парк",
            frequency=2,  # Исправлено с 'period' на 'frequency'
            reward="Кофе после пробежки",
            duration=60
        )
        from habits.tasks import update_next_reminder
        update_next_reminder(habit.id)
        habit.refresh_from_db()
        self.assertIsNotNone(habit.next_reminder)