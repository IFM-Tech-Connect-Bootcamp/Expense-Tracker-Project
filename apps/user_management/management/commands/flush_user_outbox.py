"""Django management command wrapper for user management outbox processing.

This command provides a Django-discoverable entry point that delegates
to the infrastructure layer implementation.
"""

from django.core.management.base import BaseCommand, CommandParser
from typing import Any

from apps.user_management.infrastructure.management.commands.flush_outbox import Command as InfraCommand


class Command(BaseCommand):
    """Django management command wrapper for outbox event processing."""
    
    help = "Process outbox events for delivery to external systems"
    
    def add_arguments(self, parser: CommandParser) -> None:
        """Add command arguments by delegating to infrastructure command.
        
        Args:
            parser: Command argument parser.
        """
        # Create an instance of the infrastructure command and use its arguments
        infra_command = InfraCommand()
        infra_command.add_arguments(parser)
    
    def handle(self, *args: Any, **options: Any) -> None:
        """Handle the command execution by delegating to infrastructure layer.
        
        Args:
            args: Positional arguments.
            options: Command options.
        """
        # Create and execute the infrastructure command
        infra_command = InfraCommand()
        infra_command.stdout = self.stdout
        infra_command.stderr = self.stderr
        infra_command.style = self.style
        
        # Delegate to infrastructure implementation
        infra_command.handle(*args, **options)