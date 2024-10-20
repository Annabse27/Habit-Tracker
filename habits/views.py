from rest_framework import viewsets, permissions
from .models import Habit
from .serializers import HabitSerializer
from rest_framework.response import Response
from rest_framework.decorators import action


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

    @action(detail=False, methods=['get'], permission_classes=[permissions.AllowAny])
    def public(self, request):
        """
        Эндпоинт для получения списка публичных привычек.
        """
        public_habits = Habit.objects.filter(is_public=True)
        serializer = self.get_serializer(public_habits, many=True)
        return Response(serializer.data)
