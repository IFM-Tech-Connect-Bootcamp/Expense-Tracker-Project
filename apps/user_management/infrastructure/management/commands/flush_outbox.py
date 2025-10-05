"""Django management command for outbox event processing.

This command processes pending outbox events and delivers them
to external systems. Can run once or continuously.
"""

import asyncio
import logging
import time
from typing import Any

from django.core.management.base import BaseCommand, CommandParser

from ...outbox.dispatcher import OutboxDispatcher


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """Management command for outbox event processing."""
    
    help = "Process outbox events for delivery to external systems"
    
    def add_arguments(self, parser: CommandParser) -> None:
        """Add command arguments.
        
        Args:
            parser: Command argument parser.
        """
        parser.add_argument(
            "--continuous",
            action="store_true",
            help="Run continuously processing events",
        )
        
        parser.add_argument(
            "--batch-size",
            type=int,
            default=100,
            help="Number of events to process per batch (default: 100)",
        )
        
        parser.add_argument(
            "--interval",
            type=int,
            default=30,
            help="Interval between processing cycles in seconds (default: 30)",
        )
        
        parser.add_argument(
            "--max-retries",
            type=int,
            default=3,
            help="Maximum retry attempts for failed events (default: 3)",
        )
        
        parser.add_argument(
            "--retry-delay",
            type=int,
            default=60,
            help="Delay between retries in seconds (default: 60)",
        )
    
    def handle(self, *args: Any, **options: Any) -> None:
        """Handle the command execution.
        
        Args:
            args: Positional arguments.
            options: Command options.
        """
        continuous = options["continuous"]
        batch_size = options["batch_size"]
        interval = options["interval"]
        max_retries = options["max_retries"]
        retry_delay = options["retry_delay"]
        
        self.stdout.write("📤 Starting outbox event processing...")
        
        dispatcher = OutboxDispatcher(
            batch_size=batch_size,
            max_retry_attempts=max_retries,
            retry_delay_seconds=retry_delay,
        )
        
        if continuous:
            self._run_continuous(dispatcher, interval)
        else:
            self._run_once(dispatcher)
    
    def _run_once(self, dispatcher: OutboxDispatcher) -> None:
        """Run outbox processing once.
        
        Args:
            dispatcher: Outbox event dispatcher.
        """
        try:
            asyncio.run(self._process_events(dispatcher))
            self.stdout.write(
                self.style.SUCCESS("✅ Outbox processing completed successfully")
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"❌ Outbox processing failed: {e}")
            )
            raise
    
    def _run_continuous(self, dispatcher: OutboxDispatcher, interval: int) -> None:
        """Run outbox processing continuously.
        
        Args:
            dispatcher: Outbox event dispatcher.
            interval: Interval between processing cycles in seconds.
        """
        self.stdout.write(f"🔄 Running continuously (interval: {interval}s)")
        self.stdout.write("Press Ctrl+C to stop")
        
        try:
            while True:
                try:
                    asyncio.run(self._process_events(dispatcher))
                    self.stdout.write("✅ Processing cycle completed")
                    
                except Exception as e:
                    self.stdout.write(
                        self.style.WARNING(f"⚠️  Processing cycle failed: {e}")
                    )
                    logger.error(f"Outbox processing error: {e}", exc_info=True)
                
                # Wait for next cycle
                time.sleep(interval)
                
        except KeyboardInterrupt:
            self.stdout.write("\n🛑 Stopping outbox processing...")
    
    async def _process_events(self, dispatcher: OutboxDispatcher) -> None:
        """Process outbox events.
        
        Args:
            dispatcher: Outbox event dispatcher.
        """
        start_time = time.time()
        
        processed_count = await dispatcher.dispatch_pending_events()
        
        processing_time = time.time() - start_time
        
        if processed_count > 0:
            self.stdout.write(
                f"📊 Processed {processed_count} events in {processing_time:.2f}s"
            )
        else:
            self.stdout.write("📭 No pending events to process")
        
        # Log statistics
        stats = await dispatcher.get_statistics()
        if stats:
            self.stdout.write(f"📈 Stats: {stats}")