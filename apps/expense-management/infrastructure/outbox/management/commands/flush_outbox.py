"""Django management command to flush the outbox.

This command processes pending events in the outbox, dispatching them
to external systems and marking them as processed.
"""

import logging
import time
from typing import Any

from django.core.management.base import BaseCommand

from ...dispatcher import dispatch_events

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """Management command for flushing outbox events."""

    help = (
        "Process events from outbox table, dispatching them to "
        "external systems and marking as processed."
    )

    def add_arguments(self, parser) -> None:
        """Add command line arguments.
        
        Args:
            parser: ArgumentParser instance.
        """
        parser.add_argument(
            '--batch-size',
            type=int,
            default=100,
            help="Maximum events to process per batch"
        )
        parser.add_argument(
            '--delay',
            type=int,
            default=30,
            help="Delay in seconds between batches"
        )
        parser.add_argument(
            '--continuous',
            action='store_true',
            help="Run continuously with delay between batches"
        )

    def handle(self, *args: Any, **options: Any) -> None:
        """Command execution handler.
        
        Args:
            args: Positional arguments.
            options: Named arguments.
        """
        batch_size = options['batch_size']
        delay = options['delay']
        continuous = options['continuous']

        logger.info(
            "Starting outbox flush with batch_size=%d, delay=%d, continuous=%s",
            batch_size, delay, continuous
        )

        while True:
            try:
                processed = dispatch_events(batch_size)
                logger.info(f"Processed {processed} events")

                if not continuous:
                    break

                if processed == 0:
                    time.sleep(delay)

            except KeyboardInterrupt:
                logger.info("Interrupted by user")
                break
            
            except Exception:
                logger.exception("Error processing outbox events")
                if not continuous:
                    raise