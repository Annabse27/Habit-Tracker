from django.core.exceptions import ValidationError


def validate_duration(value):
    """Проверка, что продолжительность выполнения привычки не превышает 120 секунд."""
    if value > 120:
        raise ValidationError(
            'Продолжительность выполнения не может превышать 120 секунд.')


def validate_frequency(value):
    """Проверка, что периодичность выполнения привычки не реже 1 раза в 7 дней."""
    if value < 1 or value > 7:
        raise ValidationError(
            'Привычка должна выполняться не реже 1 раза в 7 дней.')
