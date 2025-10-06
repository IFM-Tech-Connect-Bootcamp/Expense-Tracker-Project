"""Django app configuration for Expense Management.

This module configures the expense management bounded context
as a Django application.
"""

from django.apps import AppConfig


class ExpenseManagementConfig(AppConfig):
    """Configuration for the expense management app."""
    
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.expense_management'
    verbose_name = 'Expense Management'
    
    def ready(self):
        """Initialize the app when Django starts.
        
        This is where you would register signal handlers,
        perform startup checks, or initialize services.
        """
        # Import infrastructure services to ensure they're available
        try:
            from .infrastructure.config import get_config
            from .infrastructure.container import get_container
            
            # Initialize configuration
            config = get_config()
            
            # Initialize dependency injection container
            container = get_container()
            
        except ImportError:
            # In case infrastructure layer is not fully set up
            pass