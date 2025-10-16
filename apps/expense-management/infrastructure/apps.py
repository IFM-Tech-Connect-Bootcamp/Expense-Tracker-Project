"""Django app configuration for expense_management infrastructure.

This module configures the expense_management Django app and sets up:
- Domain event bus registration 
- Event subscribers
- Background tasks
"""

from django.apps import AppConfig


class ExpenseManagementInfrastructureConfig(AppConfig):
    """Django app configuration for expense management infrastructure."""
    
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'expense_management'
    verbose_name = 'Expense Management Infrastructure'

    def ready(self) -> None:
        """Initialize infrastructure components when Django starts.
        
        This method is called once Django has loaded all models and
        is ready to handle requests. We use it to:
        - Register domain event handlers
        - Initialize background services
        - Configure infrastructure dependencies
        """
        # Import domain events and services
        from ..application.event_bus import EventBus
        from ..domain.events.expense_events import ExpenseCreated, ExpenseUpdated
        from .subscribers.notify_on_expense_events import (
            on_expense_created,
            on_expense_updated,
        )
        
        # Get the global event bus instance
        event_bus = EventBus()
        
        # Register event handlers
        event_bus.subscribe(ExpenseCreated, on_expense_created)
        event_bus.subscribe(ExpenseUpdated, on_expense_updated)