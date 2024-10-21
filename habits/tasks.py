'''from celery import shared_task
from django.utils import timezone
from habits.models import Habit
import logging

logger = logging.getLogger(__name__)

# Задача для обновления данных о привычках (например, обновление даты следующего напоминания)
@shared_task
def update_habits_data():
    habits = Habit.objects.all()
    for habit in habits:
        # Логика обновления данных о привычках
        habit.next_reminder = timezone.now() + timezone.timedelta(hours=24)
        habit.save()
        logger.info(f"Updated next reminder date for habit: {habit.action}")
'''