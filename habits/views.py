from rest_framework import viewsets, permissions
from .models import Habit
from .serializers import HabitSerializer

class HabitViewSet(viewsets.ModelViewSet):
    queryset = Habit.objects.all()
    serializer_class = HabitSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Пользователь видит только свои привычки
        return Habit.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        print(f'Creating habit for user: {self.request.user}')
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        print(f'Updating habit for user: {self.request.user}')
        serializer.save(user=self.request.user)

