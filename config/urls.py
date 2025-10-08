"""
URL configuration for Expense Tracker project.

This is the main URL configuration that routes requests to appropriate
bounded context applications and provides API documentation.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/http/urls/
"""

from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)


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
                'user_management': '/api/v1/users/',
                'expense_management': '/api/v1/expenses/',
                'schema': '/api/schema/',
                'docs': '/api/docs/',
                'redoc': '/api/redoc/',
            }
        },
        'documentation': {
            'swagger': '/api/docs/',
            'redoc': '/api/redoc/',
            'openapi_schema': '/api/schema/',
        },
        'infrastructure': {
            'expense_management_commands': [
                'python manage.py flush_expense_outbox --dry-run',
                'python manage.py flush_expense_outbox --older-than-hours 48'
            ]
        }
    })


urlpatterns = [
    # Django admin
    path('admin/', admin.site.urls),
    
    # Health check
    path('health/', health_check, name='health_check'),
    
    # API root
    path('', api_root, name='api_root'),
    
    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    
    # API v1 - Bounded context URLs
    path('api/v1/users/', include('apps.user_management.presentation.urls')),
    path('api/v1/expenses/', include('apps.expense_management.presentation.urls')),
]

# Add sidecar static files serving for Swagger UI assets in development
from django.conf import settings
if settings.DEBUG:
    try:
        from drf_spectacular_sidecar import urls as sidecar_urls
        urlpatterns += [
            path('api/docs/', include(sidecar_urls)),
        ]
    except ImportError:
        # Sidecar not installed, fallback to CDN
        pass
    
    # Serve static files during development
    from django.conf.urls.static import static
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
