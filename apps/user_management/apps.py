"""
Django app configuration for User Management bounded context.

This module configures the user_management Django app with proper settings
for a modular, bounded context architecture.
"""

from django.apps import AppConfig


class UserManagementConfig(AppConfig):
    """Configuration for User Management Django app."""
    
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'user_management'
    verbose_name = 'User Management'
    
    def ready(self) -> None:
        """Called when the app is ready.
        
        This method is called after Django has finished initializing.
        It's a good place to perform app-level setup tasks.
        """
        # Import signal handlers to register them
        # from . import signals  # Uncomment when signals are implemented
        pass
