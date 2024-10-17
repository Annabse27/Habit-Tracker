from rest_framework import serializers
from .models import Habit

class HabitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Habit
        fields = ['id', 'action', 'time', 'place', 'is_pleasant', 'linked_habit', 'frequency', 'reward', 'duration', 'is_public', 'next_reminder']
        read_only_fields = ['user']  # Поле user будет только для чтения

    def validate(self, data):
        if data['is_pleasant'] and (data.get('linked_habit') or data.get('reward')):
            raise serializers.ValidationError("Приятная привычка не может иметь связанной привычки или вознаграждения.")
        if data.get('linked_habit') and data.get('reward'):
            raise serializers.ValidationError("Нельзя указать одновременно связанную привычку и вознаграждение.")
        if data['duration'] > 120:
            raise serializers.ValidationError("Время выполнения не может превышать 120 секунд.")
        if data['frequency'] < 1 or data['frequency'] > 7:
            raise serializers.ValidationError("Привычка должна повторяться не реже 1 раза в 7 дней.")
        return data
