"""Service orchestration for Expense Management application layer.

This module provides high-level service coordination for expense and category
management use cases with event bus integration.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from .commands import (
    CreateExpenseCommand,
    UpdateExpenseCommand,
    DeleteExpenseCommand,
    CreateCategoryCommand,
    UpdateCategoryCommand,
    DeleteCategoryCommand,
    GetExpenseSummaryCommand,
)

from .handlers import (
    CreateExpenseHandler,
    UpdateExpenseHandler,
    DeleteExpenseHandler,
    CreateCategoryHandler,
    UpdateCategoryHandler,
    DeleteCategoryHandler,
    GetExpenseSummaryHandler,
)

from .dto import ExpenseDTO, CategoryDTO, ExpenseSummaryDTO
from .event_bus import event_bus
from .subscribers import log_expense_events
from .errors import ApplicationError

if TYPE_CHECKING:
    from ..domain.repositories.expense_repository import ExpenseRepository
    from ..domain.repositories.category_repository import CategoryRepository

logger = logging.getLogger(__name__)


class ExpenseManagementService:
    """High-level service for expense management operations.
    
    This service coordinates all expense and category management use cases
    by orchestrating command handlers and managing event publication.
    It serves as the main entry point for the application layer.
    """
    
    def __init__(
        self,
        expense_repository: "ExpenseRepository",
        category_repository: "CategoryRepository",
    ) -> None:
        """Initialize the expense management service.
        
        Args:
            expense_repository: Repository for expense persistence operations.
            category_repository: Repository for category persistence operations.
        """
        self._expense_repository = expense_repository
        self._category_repository = category_repository
        
        # Initialize handlers
        self._create_expense_handler = CreateExpenseHandler(
            expense_repository=expense_repository,
            category_repository=category_repository
        )
        
        self._update_expense_handler = UpdateExpenseHandler(
            expense_repository=expense_repository,
            category_repository=category_repository
        )
        
        self._delete_expense_handler = DeleteExpenseHandler(
            expense_repository=expense_repository
        )
        
        self._create_category_handler = CreateCategoryHandler(
            category_repository=category_repository
        )
        
        self._update_category_handler = UpdateCategoryHandler(
            category_repository=category_repository
        )
        
        self._delete_category_handler = DeleteCategoryHandler(
            category_repository=category_repository,
            expense_repository=expense_repository
        )
        
        self._get_expense_summary_handler = GetExpenseSummaryHandler(
            expense_repository=expense_repository,
            category_repository=category_repository
        )
        
        # Wire up event subscribers
        self._setup_event_subscribers()
        
        logger.info("ExpenseManagementService initialized successfully")
    
    def _setup_event_subscribers(self) -> None:
        """Set up event subscribers for domain events."""
        from ..domain.events.expense_events import ExpenseCreated, ExpenseUpdated, ExpenseDeleted
        from ..domain.events.category_events import CategoryCreated, CategoryUpdated, CategoryDeleted
        
        # Subscribe to all expense events
        event_bus.subscribe(ExpenseCreated, log_expense_events)
        event_bus.subscribe(ExpenseUpdated, log_expense_events)
        event_bus.subscribe(ExpenseDeleted, log_expense_events)
        
        # Subscribe to all category events
        event_bus.subscribe(CategoryCreated, log_expense_events)
        event_bus.subscribe(CategoryUpdated, log_expense_events)
        event_bus.subscribe(CategoryDeleted, log_expense_events)
        
        logger.debug("Event subscribers configured successfully")
    
    # Expense operations
    
    def create_expense(self, command: CreateExpenseCommand) -> ExpenseDTO:
        """Create a new expense.
        
        Args:
            command: Expense creation command.
            
        Returns:
            Created expense DTO.
            
        Raises:
            ApplicationError: If expense creation fails.
        """
        logger.debug(f"Processing expense creation command for user {command.user_id}")
        result = self._create_expense_handler.handle(command)
        
        # Publish domain events
        event_bus.publish_all(result.events)
        
        return result.expense_dto
    
    def update_expense(self, command: UpdateExpenseCommand) -> ExpenseDTO:
        """Update an existing expense.
        
        Args:
            command: Expense update command.
            
        Returns:
            Updated expense DTO.
            
        Raises:
            ApplicationError: If expense update fails.
        """
        logger.debug(f"Processing expense update command for expense {command.expense_id}")
        result = self._update_expense_handler.handle(command)
        
        # Publish domain events
        event_bus.publish_all(result.events)
        
        return result.expense_dto
    
    def delete_expense(self, command: DeleteExpenseCommand) -> str:
        """Delete an expense.
        
        Args:
            command: Expense deletion command.
            
        Returns:
            ID of the deleted expense.
            
        Raises:
            ApplicationError: If expense deletion fails.
        """
        logger.debug(f"Processing expense deletion command for expense {command.expense_id}")
        result = self._delete_expense_handler.handle(command)
        
        # Publish domain events
        event_bus.publish_all(result.events)
        
        return result.deleted_expense_id
    
    # Category operations
    
    def create_category(self, command: CreateCategoryCommand) -> CategoryDTO:
        """Create a new category.
        
        Args:
            command: Category creation command.
            
        Returns:
            Created category DTO.
            
        Raises:
            ApplicationError: If category creation fails.
        """
        logger.debug(f"Processing category creation command for user {command.user_id}")
        result = self._create_category_handler.handle(command)
        
        # Publish domain events
        event_bus.publish_all(result.events)
        
        return result.category_dto
    
    def update_category(self, command: UpdateCategoryCommand) -> CategoryDTO:
        """Update an existing category.
        
        Args:
            command: Category update command.
            
        Returns:
            Updated category DTO.
            
        Raises:
            ApplicationError: If category update fails.
        """
        logger.debug(f"Processing category update command for category {command.category_id}")
        result = self._update_category_handler.handle(command)
        
        # Publish domain events
        event_bus.publish_all(result.events)
        
        return result.category_dto
    
    def delete_category(self, command: DeleteCategoryCommand) -> str:
        """Delete a category.
        
        Args:
            command: Category deletion command.
            
        Returns:
            ID of the deleted category.
            
        Raises:
            ApplicationError: If category deletion fails.
        """
        logger.debug(f"Processing category deletion command for category {command.category_id}")
        result = self._delete_category_handler.handle(command)
        
        # Publish domain events
        event_bus.publish_all(result.events)
        
        return result.deleted_category_id
    
    # Query operations
    
    def get_expense_summary(self, command: GetExpenseSummaryCommand) -> ExpenseSummaryDTO:
        """Get expense summary and analytics.
        
        Args:
            command: Expense summary query command.
            
        Returns:
            Comprehensive expense summary DTO.
            
        Raises:
            ApplicationError: If summary generation fails.
        """
        logger.debug(f"Processing expense summary query for user {command.user_id}")
        result = self._get_expense_summary_handler.handle(command)
        
        return result.summary_dto
    
    # Service utilities
    
    def get_event_bus_statistics(self) -> dict:
        """Get event bus statistics for monitoring.
        
        Returns:
            Dictionary containing event bus statistics.
        """
        return event_bus.get_statistics()