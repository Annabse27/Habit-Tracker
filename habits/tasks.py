import logging
from celery import shared_task
from .models import Habit

# Настраиваем логгер для tasks
logger = logging.getLogger(__name__)


@shared_task
def update_next_reminder(habit_id):
    try:
        habit = Habit.objects.get(id=habit_id)
        habit.calculate_next_reminder()  # Обновляем дату следующего напоминания
    except Habit.DoesNotExist:
        logger.info(f'Habit with id {habit_id} does not exist')
