"""
URL configuration for User Management API endpoints.

This module defines the URL patterns for the user management presentation layer,
mapping HTTP endpoints to their corresponding view functions.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    register_user,
    authenticate_user,
    get_current_user,
    update_profile,
    change_password,
    deactivate_user,
    user_health_check,
)


# Define URL patterns for the user management API
urlpatterns = [
    # Health check
    path('health/', user_health_check, name='user_health_check'),
    
    # Authentication endpoints
    path('auth/register/', register_user, name='register_user'),
    path('auth/login/', authenticate_user, name='authenticate_user'),
    
    # User profile endpoints (requires authentication)
    path('profile/', get_current_user, name='get_current_user'),
    path('profile/update/', update_profile, name='update_profile'),
    path('profile/change-password/', change_password, name='change_password'),
    path('profile/deactivate/', deactivate_user, name='deactivate_user'),
]

# API versioning - these URLs will be prefixed with /api/v1/users/
app_name = 'user_management'