from django.db import models
from django.core.exceptions import ValidationError
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from .validators import validate_duration, validate_frequency  # Импортируем валидаторы


class Habit(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='habits')
    action = models.CharField(max_length=255, help_text="Описание действия")
    time = models.TimeField(help_text="Время выполнения привычки")
    place = models.CharField(max_length=255, help_text="Место выполнения привычки")
    is_pleasant = models.BooleanField(default=False, help_text="Это приятная привычка?")
    linked_habit = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='linked_to',
                                     help_text="Связанная привычка (для полезной привычки)")
    frequency = models.PositiveIntegerField(default=1, help_text="Периодичность выполнения в днях", validators=[validate_frequency])
    reward = models.CharField(max_length=255, null=True, blank=True, help_text="Вознаграждение за выполнение")
    duration = models.PositiveIntegerField(help_text="Время на выполнение в секундах", validators=[validate_duration])
    is_public = models.BooleanField(default=False, help_text="Привычка публичная?")
    next_reminder = models.DateTimeField(null=True, blank=True, help_text="Дата и время следующего напоминания")

    class Meta:
        ordering = ['next_reminder']
        verbose_name = 'Привычка'
        verbose_name_plural = 'Привычки'

    def clean(self):
        # Проверка, что у приятной привычки нет связанной привычки или вознаграждения
        if self.is_pleasant and (self.linked_habit or self.reward):
            raise ValidationError('Приятная привычка не может иметь связанной привычки или вознаграждения.')

        # Проверка, что у привычки не указаны одновременно связанная привычка и вознаграждение
        if self.linked_habit and self.reward:
            raise ValidationError('Нельзя указать одновременно связанную привычку и вознаграждение.')

        # Проверка на продолжительность выполнения привычки (не больше 120 секунд)
        if self.duration > 120:
            raise ValidationError('Время выполнения не может превышать 120 секунд.')

        # Проверка на минимальную периодичность (не реже 1 раза в 7 дней)
        if self.frequency < 1 or self.frequency > 7:
            raise ValidationError('Привычка должна повторяться не реже 1 раза в 7 дней.')

    def calculate_next_reminder(self):
        """
        Вычисляет и устанавливает дату следующего напоминания
        на основе текущей даты и времени выполнения привычки.
        """
        now = timezone.now()
        next_reminder_date = now + timedelta(days=self.frequency)
        self.next_reminder = timezone.make_aware(
            timezone.datetime.combine(next_reminder_date, self.time)
        )
        self.save()

    def save(self, *args, **kwargs):
        """Логика для расчета первого напоминания"""
        if not self.next_reminder:
            self.next_reminder = timezone.now() + timezone.timedelta(days=self.frequency)
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.action} ({self.user})'
