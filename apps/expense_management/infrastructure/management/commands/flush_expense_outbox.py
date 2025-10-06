"""Django management command for expense management outbox event processing.

This command processes pending outbox events and delivers them
to external systems. Can run once or continuously. Also provides
cleanup functionality for processed events.
"""

from __future__ import annotations

import asyncio
import logging
import time
from typing import Any, Dict
from datetime import datetime, timedelta

from django.core.management.base import BaseCommand, CommandParser, CommandError
from django.db import transaction

from ...orm.models import OutboxEvent
from ...outbox.dispatcher import create_outbox_dispatcher

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """Django management command for comprehensive expense outbox management."""
    
    help = "Process and manage expense management outbox events"
    
    def add_arguments(self, parser: CommandParser) -> None:
        """Add command line arguments.
        
        Args:
            parser: Django argument parser.
        """
        # Processing options
        parser.add_argument(
            '--continuous',
            action='store_true',
            help='Run continuously processing events'
        )
        
        parser.add_argument(
            '--batch-size',
            type=int,
            default=100,
            help='Number of events to process per batch (default: 100)'
        )
        
        parser.add_argument(
            '--interval',
            type=int,
            default=30,
            help='Interval between processing cycles in seconds (default: 30)'
        )
        
        parser.add_argument(
            '--max-retries',
            type=int,
            default=3,
            help='Maximum retry attempts for failed events (default: 3)'
        )
        
        parser.add_argument(
            '--retry-delay',
            type=int,
            default=60,
            help='Delay between retries in seconds (default: 60)'
        )
        
        # Operation modes
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
        
        # Legacy cleanup options (for backward compatibility)
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be deleted without actually deleting'
        )
        
        parser.add_argument(
            '--older-than-hours',
            type=int,
            default=24,
            help='Delete events older than specified hours (default: 24) - legacy option'
        )
        
        # Information options
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
    
    def handle(self, *args: Any, **options: Any) -> None:
        """Handle the command execution.
        
        Args:
            args: Positional arguments.
            options: Command options.
        """
        # Configure logging
        if options['verbose']:
            logging.basicConfig(level=logging.DEBUG)
        else:
            logging.basicConfig(level=logging.INFO)
        
        try:
            # Determine operation mode
            if options['stats']:
                self._show_statistics()
            elif options['cleanup'] or options['dry_run']:
                # Use new cleanup if --cleanup specified, otherwise legacy
                if options['cleanup']:
                    asyncio.run(self._cleanup_events_advanced(options['cleanup_days'], options['dry_run']))
                else:
                    self._cleanup_events_legacy(options['older_than_hours'], options['dry_run'])
            elif options['retry_failed']:
                asyncio.run(self._retry_failed_events(options))
            elif options['continuous']:
                self._run_continuous_processing(options)
            else:
                # Single processing run
                self._run_single_processing(options)
            
        except Exception as e:
            logger.error(f"Command execution failed: {e}")
            raise CommandError(f"Failed to process expense outbox events: {e}") from e
    
    def _run_single_processing(self, options: Dict[str, Any]) -> None:
        """Run outbox processing once.
        
        Args:
            options: Command options.
        """
        self.stdout.write("📤 Starting expense outbox event processing...")
        
        try:
            dispatcher = self._create_dispatcher(options)
            asyncio.run(self._process_events(dispatcher))
            
            self.stdout.write(
                self.style.SUCCESS("✅ Expense outbox processing completed successfully")
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"❌ Expense outbox processing failed: {e}")
            )
            raise
    
    def _run_continuous_processing(self, options: Dict[str, Any]) -> None:
        """Run outbox processing continuously.
        
        Args:
            options: Command options.
        """
        interval = options['interval']
        
        self.stdout.write(f"🔄 Running expense outbox processing continuously (interval: {interval}s)")
        self.stdout.write("Press Ctrl+C to stop")
        
        dispatcher = self._create_dispatcher(options)
        
        try:
            while True:
                try:
                    asyncio.run(self._process_events(dispatcher))
                    self.stdout.write("✅ Processing cycle completed")
                    
                except Exception as e:
                    self.stdout.write(
                        self.style.WARNING(f"⚠️ Processing cycle failed: {e}")
                    )
                    logger.error(f"Expense outbox processing error: {e}", exc_info=True)
                
                # Wait for next cycle
                time.sleep(interval)
                
        except KeyboardInterrupt:
            self.stdout.write("\n🛑 Stopping expense outbox processing...")
    
    async def _process_events(self, dispatcher) -> None:
        """Process outbox events.
        
        Args:
            dispatcher: Outbox event dispatcher.
        """
        start_time = time.time()
        
        try:
            processed_count = await dispatcher.dispatch_pending_events()
            processing_time = time.time() - start_time
            
            if processed_count > 0:
                self.stdout.write(
                    f"📊 Processed {processed_count} expense events in {processing_time:.2f}s"
                )
            else:
                self.stdout.write("📭 No pending expense events to process")
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"Failed to process events: {e}")
            )
            raise
    
    async def _retry_failed_events(self, options: Dict[str, Any]) -> None:
        """Retry previously failed events.
        
        Args:
            options: Command options.
        """
        self.stdout.write("🔄 Starting failed expense events retry operation...")
        
        try:
            dispatcher = self._create_dispatcher(options)
            stats = await dispatcher.retry_failed_events()
            
            self.stdout.write(
                self.style.SUCCESS(
                    f"Failed expense events retry completed:\n"
                    f"  - Processed: {stats.get('processed', 0)} events\n"
                    f"  - Failed: {stats.get('failed', 0)} events\n"
                    f"  - Skipped: {stats.get('skipped', 0)} events"
                )
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"Failed events retry failed: {e}")
            )
            raise
    
    async def _cleanup_events_advanced(self, cleanup_days: int, dry_run: bool = False) -> None:
        """Clean up old processed events (advanced mode).
        
        Args:
            cleanup_days: Number of days to keep processed events.
            dry_run: If True, show what would be deleted without deleting.
        """
        self.stdout.write(f"🧹 Starting cleanup of expense events older than {cleanup_days} days...")
        
        try:
            dispatcher = self._create_dispatcher({})
            
            if dry_run:
                # Count what would be deleted
                cutoff_time = datetime.now() - timedelta(days=cleanup_days)
                count = OutboxEvent.objects.filter(
                    processed_at__isnull=False,
                    processed_at__lt=cutoff_time
                ).count()
                
                self.stdout.write(
                    self.style.WARNING(
                        f"DRY RUN: Would delete {count} processed expense events "
                        f"older than {cleanup_days} days"
                    )
                )
            else:
                deleted_count = await dispatcher.cleanup_processed_events(cleanup_days)
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Expense events cleanup completed: {deleted_count} events deleted"
                    )
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"Cleanup failed: {e}")
            )
            raise
    
    def _cleanup_events_legacy(self, hours: int, dry_run: bool = False) -> None:
        """Clean up old processed events (legacy mode for backward compatibility).
        
        Args:
            hours: Number of hours to keep processed events.
            dry_run: If True, show what would be deleted without deleting.
        """
        self.stdout.write(f"🧹 Starting legacy cleanup of expense events older than {hours} hours...")
        
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        # Find events to delete - only processed events older than cutoff
        events_to_delete = OutboxEvent.objects.filter(
            processed_at__isnull=False,
            processed_at__lt=cutoff_time
        )
        
        count = events_to_delete.count()
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    f"DRY RUN: Would delete {count} processed expense outbox events "
                    f"older than {hours} hours"
                )
            )
            return
        
        if count == 0:
            self.stdout.write(
                self.style.SUCCESS("No processed expense outbox events to delete")
            )
            return
        
        # Delete the events
        with transaction.atomic():
            deleted_count, _ = events_to_delete.delete()
        
        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully deleted {deleted_count} processed expense outbox events"
            )
        )
    
    def _show_statistics(self) -> None:
        """Show outbox statistics."""
        try:
            # Calculate statistics directly from database
            total_events = OutboxEvent.objects.count()
            processed_events = OutboxEvent.objects.filter(processed_at__isnull=False).count()
            pending_events = OutboxEvent.objects.filter(processed_at__isnull=True).count()
            failed_events = OutboxEvent.objects.filter(
                processed_at__isnull=True,
                attempts__gt=0
            ).count()
            
            # Get event type distribution
            event_types = OutboxEvent.objects.values_list('event_type', flat=True).distinct()
            
            # Calculate processing rate safely
            processing_rate = (processed_events / total_events * 100) if total_events > 0 else 0
            
            self.stdout.write(
                self.style.SUCCESS(
                    f"Expense Management Outbox Statistics:\n"
                    f"  - Total events: {total_events}\n"
                    f"  - Processed events: {processed_events}\n"
                    f"  - Pending events: {pending_events}\n"
                    f"  - Failed events: {failed_events}\n"
                    f"  - Event types: {', '.join(event_types) if event_types else 'None'}\n"
                    f"  - Processing rate: {processing_rate:.1f}%"
                )
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"Failed to get statistics: {e}")
            )
            raise CommandError(f"Failed to get statistics: {e}") from e
    
    def _create_dispatcher(self, options: Dict[str, Any]):
        """Create outbox dispatcher with specified options.
        
        Args:
            options: Command options.
            
        Returns:
            Configured outbox dispatcher.
        """
        try:
            return create_outbox_dispatcher(
                max_retries=options.get('max_retries', 3),
                retry_delay_minutes=options.get('retry_delay', 60) // 60,
                batch_size=options.get('batch_size', 100)
            )
        except Exception as e:
            # Fallback to basic configuration if dispatcher creation fails
            logger.warning(f"Failed to create advanced dispatcher: {e}")
            return None