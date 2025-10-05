"""Django app configuration for user_management infrastructure.

This module configures the user_management Django app and sets up:
- Domain event bus registration
- Infrastructure services  
- Event subscribers
- Background tasks
"""

from typing import TYPE_CHECKING

from django.apps import AppConfig
from django.conf import settings

if TYPE_CHECKING:
    from ..domain.events.user_events import UserRegistered


class UserManagementInfrastructureConfig(AppConfig):
    """Django app configuration for user management infrastructure."""
    
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'user_management'
    verbose_name = 'User Management Infrastructure'

    def ready(self) -> None:
        """Initialize infrastructure components when Django starts.
        
        This method is called once Django has loaded all models and
        is ready to handle requests. We use it to:
        - Register domain event handlers
        - Initialize background services
        - Configure infrastructure dependencies
        """
        # Import domain events and services
        from ..domain.events.user_events import UserRegistered
        from ..application.event_bus import EventBus
        from .subscribers.notify_on_user_events import (
            on_user_registered,
            on_user_password_changed,
            on_user_profile_updated, 
            on_user_deactivated,
        )
        
        # Get the global event bus instance
        event_bus = EventBus.get_instance()
        
        # Register event handlers
        event_bus.subscribe(UserRegistered, on_user_registered)
        
        # Register handlers for other user events when they exist
        # event_bus.subscribe(UserPasswordChanged, on_user_password_changed)
        # event_bus.subscribe(UserProfileUpdated, on_user_profile_updated)
        # event_bus.subscribe(UserDeactivated, on_user_deactivated)
        
        # Start background outbox processing if enabled
        if getattr(settings, 'OUTBOX_AUTO_PROCESS', False):
            self._start_outbox_processing()

    def _start_outbox_processing(self) -> None:
        """Start background outbox event processing.
        
        This starts a background task to periodically flush outbox events
        to external systems. Should only be enabled in production environments
        where reliable event delivery is required.
        """
        import asyncio
        import threading
        from .outbox.dispatcher import OutboxDispatcher
        
        def run_outbox_processor():
            """Background thread function for outbox processing."""
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            dispatcher = OutboxDispatcher()
            
            # Run outbox processing every 30 seconds
            async def process_loop():
                while True:
                    try:
                        await dispatcher.dispatch_pending_events()
                        await asyncio.sleep(30)
                    except Exception as e:
                        # Log error but keep processing
                        import logging
                        logger = logging.getLogger(__name__)
                        logger.error(f"Outbox processing error: {e}")
                        await asyncio.sleep(60)  # Wait longer on error
            
            loop.run_until_complete(process_loop())
        
        # Start background thread for outbox processing
        thread = threading.Thread(target=run_outbox_processor, daemon=True)
        thread.start()