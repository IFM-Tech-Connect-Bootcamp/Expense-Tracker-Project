"""
URL configuration for Expense Tracker project.

This is the main URL configuration that routes requests to appropriate
bounded context applications.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/http/urls/
"""

from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse


def health_check(request):
    """Health check endpoint for monitoring."""
    return JsonResponse({
        'status': 'healthy',
        'service': 'expense-tracker-api',
        'version': '1.0.0'
    })


def api_root(request):
    """API root endpoint with available endpoints."""
    return JsonResponse({
        'message': 'Expense Tracker API',
        'version': '1.0.0',
        'endpoints': {
            'health': '/health/',
            'admin': '/admin/',
            'api': {
                'user_management': '/api/users/',
            }
        }
    })


urlpatterns = [
    # Django admin
    path('admin/', admin.site.urls),
    
    # Health check
    path('health/', health_check, name='health_check'),
    
    # API root
    path('', api_root, name='api_root'),
    
    # Bounded context URLs
    path('api/users/', include('user_management.urls')),
]
