"""Django management command for flushing outbox events.

This command processes unprocessed outbox events and delivers them
to external systems. Can be run manually or scheduled via cron.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any, Dict

from django.core.management.base import BaseCommand, CommandError

from ...dispatcher import create_outbox_dispatcher

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """Django management command to flush user management outbox events."""
    
    help = "Process and deliver unprocessed outbox events for user management"
    
    def add_arguments(self, parser) -> None:
        """Add command line arguments.
        
        Args:
            parser: Django argument parser.
        """
        parser.add_argument(
            '--max-retries',
            type=int,
            default=3,
            help='Maximum number of retry attempts per event (default: 3)'
        )
        
        parser.add_argument(
            '--retry-delay',
            type=int,
            default=5,
            help='Delay between retries in minutes (default: 5)'
        )
        
        parser.add_argument(
            '--batch-size',
            type=int,
            default=50,
            help='Number of events to process in each batch (default: 50)'
        )
        
        parser.add_argument(
            '--retry-failed',
            action='store_true',
            help='Retry previously failed events'
        )
        
        parser.add_argument(
            '--cleanup',
            action='store_true',
            help='Clean up old processed events'
        )
        
        parser.add_argument(
            '--cleanup-days',
            type=int,
            default=30,
            help='Remove processed events older than this many days (default: 30)'
        )
        
        parser.add_argument(
            '--stats',
            action='store_true',
            help='Show outbox statistics'
        )
        
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Enable verbose logging'
        )
    
    def handle(self, *args, **options) -> None:
        """Handle the management command execution.
        
        Args:
            *args: Positional arguments.
            **options: Command options.
            
        Raises:
            CommandError: If command execution fails.
        """
        # Configure logging
        if options['verbose']:
            logging.basicConfig(level=logging.DEBUG)
        else:
            logging.basicConfig(level=logging.INFO)
        
        try:
            # Create dispatcher with specified options
            dispatcher = create_outbox_dispatcher(
                max_retries=options['max_retries'],
                retry_delay_minutes=options['retry_delay'],
                batch_size=options['batch_size']
            )
            
            # Register default handlers (this would be done in a real implementation)
            # self._register_handlers(dispatcher)
            
            # Run the appropriate operation
            if options['stats']:
                self._show_statistics(dispatcher)
            elif options['cleanup']:
                asyncio.run(self._cleanup_events(dispatcher, options['cleanup_days']))
            elif options['retry_failed']:
                asyncio.run(self._retry_failed_events(dispatcher))
            else:
                asyncio.run(self._flush_outbox(dispatcher))
            
        except Exception as e:
            logger.error(f"Command execution failed: {e}")
            raise CommandError(f"Failed to process outbox events: {e}") from e
    
    async def _flush_outbox(self, dispatcher) -> None:
        """Flush the outbox by processing unprocessed events.
        
        Args:
            dispatcher: Outbox dispatcher instance.
        """
        self.stdout.write("Starting outbox flush operation...")
        
        try:
            stats = await dispatcher.flush_outbox()
            
            self.stdout.write(
                self.style.SUCCESS(
                    f"Outbox flush completed successfully:\n"
                    f"  - Processed: {stats['processed']} events\n"
                    f"  - Failed: {stats['failed']} events\n"
                    f"  - Skipped: {stats['skipped']} events"
                )
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"Outbox flush failed: {e}")
            )
            raise
    
    async def _retry_failed_events(self, dispatcher) -> None:
        """Retry previously failed events.
        
        Args:
            dispatcher: Outbox dispatcher instance.
        """
        self.stdout.write("Starting failed events retry operation...")
        
        try:
            stats = await dispatcher.retry_failed_events()
            
            self.stdout.write(
                self.style.SUCCESS(
                    f"Failed events retry completed:\n"
                    f"  - Processed: {stats['processed']} events\n"
                    f"  - Failed: {stats['failed']} events\n"
                    f"  - Skipped: {stats['skipped']} events"
                )
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"Failed events retry failed: {e}")
            )
            raise
    
    async def _cleanup_events(self, dispatcher, cleanup_days: int) -> None:
        """Clean up old processed events.
        
        Args:
            dispatcher: Outbox dispatcher instance.
            cleanup_days: Number of days to keep processed events.
        """
        self.stdout.write(f"Starting cleanup of events older than {cleanup_days} days...")
        
        try:
            deleted_count = await dispatcher.cleanup_processed_events(cleanup_days)
            
            self.stdout.write(
                self.style.SUCCESS(
                    f"Cleanup completed: {deleted_count} events deleted"
                )
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"Cleanup failed: {e}")
            )
            raise
    
    def _show_statistics(self, dispatcher) -> None:
        """Show outbox statistics.
        
        Args:
            dispatcher: Outbox dispatcher instance.
        """
        try:
            stats = dispatcher.get_statistics()
            
            self.stdout.write(
                self.style.SUCCESS(
                    f"Outbox Statistics:\n"
                    f"  - Total events: {stats['total_events']}\n"
                    f"  - Processed events: {stats['processed_events']}\n"
                    f"  - Pending events: {stats['pending_events']}\n"
                    f"  - Failed events: {stats['failed_events']}\n"
                    f"  - Registered handlers: {', '.join(stats['registered_handlers'])}\n"
                    f"  - Max retries: {stats['max_retries']}\n"
                    f"  - Retry delay: {stats['retry_delay_minutes']} minutes\n"
                    f"  - Batch size: {stats['batch_size']}"
                )
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"Failed to get statistics: {e}")
            )
            raise CommandError(f"Failed to get statistics: {e}") from e
    
    def _register_handlers(self, dispatcher) -> None:
        """Register event handlers with the dispatcher.
        
        This is where you would register actual event handlers
        for different types of outbox events.
        
        Args:
            dispatcher: Outbox dispatcher instance.
        """
        # Example of how handlers would be registered:
        # from ..handlers import EmailNotificationHandler, WebhookHandler
        # 
        # dispatcher.register_handler('UserRegistered', EmailNotificationHandler())
        # dispatcher.register_handler('UserDeactivated', WebhookHandler())
        
        pass