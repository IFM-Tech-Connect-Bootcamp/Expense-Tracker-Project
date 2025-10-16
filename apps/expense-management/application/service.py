"""Application service for expense management.

This module provides the main service interface for expense management
operations, delegating to appropriate handlers and managing events.
"""

from __future__ import annotations

from typing import List, Optional

from ..domain.repositories.expense_repository import ExpenseRepository
from ..domain.repositories.category_repository import CategoryRepository

from .event_bus import EventBus
from .dto.expense_dto import ExpenseDTO
from .commands.expense_commands import CreateExpenseCommand, UpdateExpenseCommand
from .handlers.create_expense import CreateExpenseHandler
from .handlers.update_expense import UpdateExpenseHandler


class ExpenseService:
    """Service orchestrating expense management use cases."""
    
    def __init__(
        self,
        expense_repo: ExpenseRepository,
        category_repo: CategoryRepository,
        event_bus: Optional[EventBus] = None
    ):
        """Initialize the expense service.
        
        Args:
            expense_repo: Repository for expense operations
            category_repo: Repository for category operations
            event_bus: Optional event bus for publishing domain events
        """
        self._expense_repo = expense_repo
        self._category_repo = category_repo
        self._event_bus = event_bus or EventBus()
        
        # Initialize handlers
        self._create_handler = CreateExpenseHandler(self._expense_repo, self._category_repo)
        self._update_handler = UpdateExpenseHandler(self._expense_repo, self._category_repo)
    
    def create_expense(self, cmd: CreateExpenseCommand) -> ExpenseDTO:
        """Create a new expense.
        
        Args:
            cmd: Command containing new expense details
            
        Returns:
            DTO representing the created expense
        """
        result = self._create_handler.handle(cmd)
        
        # Publish events if any handlers are subscribed
        if result.events:
            for event in result.events:
                self._event_bus.publish(event)
            
        return result.expense_dto
    
    def update_expense(self, cmd: UpdateExpenseCommand) -> ExpenseDTO:
        """Update an existing expense.
        
        Args:
            cmd: Command containing expense updates
            
        Returns:
            DTO representing the updated expense
        """
        result = self._update_handler.handle(cmd)
        
        # Publish events if any handlers are subscribed
        if result.events:
            for event in result.events:
                self._event_bus.publish(event)
            
        return result.expense_dto
    
    def list_user_expenses(self, user_id: str) -> List[ExpenseDTO]:
        """List all expenses for a user.
        
        Args:
            user_id: ID of the user to list expenses for
            
        Returns:
            List of expense DTOs
        """
        expenses = self._expense_repo.list_by_user(user_id)
        return [
            ExpenseDTO(
                expense_id=e.expense_id,
                user_id=str(e.user_id),
                amount_tzs=float(e.amount_tzs.value),
                description=str(e.description.value),
                date=str(e.date.value),
                category_id=str(e.category_id) if e.category_id else None,
            )
            for e in expenses
        ]
