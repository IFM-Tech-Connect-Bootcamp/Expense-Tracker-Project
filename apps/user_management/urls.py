"""
URL configuration for User Management bounded context.

This module defines the URL patterns for the user management API endpoints.
All endpoints are prefixed with 'api/users/' in the main URL configuration.
"""

from django.urls import path, include
from django.http import JsonResponse


def user_management_root(request):
    """User management API root endpoint."""
    return JsonResponse({
        'message': 'User Management API',
        'version': '1.0.0',
        'endpoints': {
            'auth': {
                'register': '/api/users/auth/register/',
                'login': '/api/users/auth/login/',
                'logout': '/api/users/auth/logout/',
            },
            'profile': {
                'me': '/api/users/profile/me/',
                'update': '/api/users/profile/me/',
                'change_password': '/api/users/profile/change-password/',
            }
        }
    })


# Import views when they're available
try:
    from .presentation.api_views import RegisterView
    VIEWS_AVAILABLE = True
except ImportError:
    VIEWS_AVAILABLE = False

app_name = 'user_management'

urlpatterns = [
    # Root endpoint
    path('', user_management_root, name='root'),
]

# Add actual endpoints only if views are available
if VIEWS_AVAILABLE:
    urlpatterns.extend([
        # Authentication endpoints
        path('auth/register/', RegisterView.as_view(), name='register'),
        # Uncomment as views are implemented:
        # path('auth/login/', LoginView.as_view(), name='login'),
        # path('auth/logout/', LogoutView.as_view(), name='logout'),
        
        # User profile endpoints
        # path('profile/me/', ProfileView.as_view(), name='profile'),
        # path('profile/change-password/', ChangePasswordView.as_view(), name='change_password'),
    ])
else:
    # Fallback endpoints when views are not yet available
    def not_implemented(request):
        return JsonResponse({
            'error': 'This endpoint is not yet implemented',
            'status': 'coming_soon'
        }, status=501)
    
    urlpatterns.extend([
        path('auth/register/', not_implemented, name='register_placeholder'),
        path('auth/login/', not_implemented, name='login_placeholder'),
    ])