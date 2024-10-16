from celery import shared_task
from django.utils import timezone
from .models import Habit


@shared_task
def update_next_reminder(habit_id):
    try:
        habit = Habit.objects.get(id=habit_id)
        habit.calculate_next_reminder()  # Обновляем дату следующего напоминания
    except Habit.DoesNotExist:
        print(f'Habit with id {habit_id} does not exist')
