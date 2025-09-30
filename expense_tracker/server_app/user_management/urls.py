# usermanagement/urls.py
from django.urls import path
from .presentation.api_views import RegisterView #, LoginView # and others

urlpatterns = [
    # API Endpoints from Section 8
    path('auth/register', RegisterView.as_view(), name='register'),
    # path('auth/login', LoginView.as_view(), name='login'),
    # path('users/me', ProfileView.as_view(), name='profile'),
    # path('users/me/password', ChangePasswordView.as_view(), name='change_password'),
]