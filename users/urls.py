from django.urls import path
from .views import UserRegistrationView
from .views import UserLoginView


urlpatterns = [
       path('register/', UserRegistrationView.as_view(), name='user-registration'),
       path('login/', UserLoginView.as_view(), name='user-login'),
   ]
