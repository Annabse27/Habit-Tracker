from rest_framework import viewsets, permissions
from .models import Habit
from .serializers import HabitSerializer
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import status
from django.shortcuts import get_object_or_404


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
        habit = serializer.instance
        if habit.user != self.request.user:
            return Response({"detail": "Вы не можете редактировать чужие привычки."}, status=status.HTTP_403_FORBIDDEN)
        print(f'Updating habit for user: {self.request.user}')
        serializer.save(user=self.request.user)

    def perform_destroy(self, instance):
        habit = get_object_or_404(Habit, id=instance.id)
        if habit.user != self.request.user:
            return Response({"detail": "Вы не можете удалять чужие привычки."}, status=status.HTTP_403_FORBIDDEN)
        habit.delete()

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.user != request.user:
            return Response({"detail": "Вы не можете просматривать чужие привычки."}, status=status.HTTP_403_FORBIDDEN)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], permission_classes=[permissions.AllowAny])
    def public(self, request):
        """
        Эндпоинт для получения списка публичных привычек.
        """
        public_habits = Habit.objects.filter(is_public=True)
        serializer = self.get_serializer(public_habits, many=True)
        return Response(serializer.data)
