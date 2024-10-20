from rest_framework.routers import DefaultRouter
from .views import HabitViewSet
from django.urls import path, include


router = DefaultRouter()
router.register(r'habits', HabitViewSet, basename='habit')

urlpatterns = [
    path('', include(router.urls)),
    path('habits/public/', HabitViewSet.as_view({'get': 'public'}), name='public-habits')
]
