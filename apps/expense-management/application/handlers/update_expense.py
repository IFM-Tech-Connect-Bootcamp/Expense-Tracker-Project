"""Update expense handler.

This module contains the handler for expense update use cases.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Protocol

from ...domain.entities.expense import Expense
from ...domain.events.expense_events import DomainEvent, ExpenseUpdated
from ...domain.repositories.expense_repository import ExpenseRepository
from ...domain.repositories.category_repository import CategoryRepository
from ...domain.value_objects.user.user_id import UserId
from ...domain.value_objects.expense.amount_tzs import AmountTZS
from ...domain.value_objects.expense.description import Description
from ...domain.value_objects.expense.date import Date
from ...domain.value_objects.category.category_id import CategoryId
from ...domain.value_objects.expense.expense_id import ExpenseId

from ..commands.expense_commands import UpdateExpenseCommand
from ..dto.expense_dto import ExpenseDTO
from ..errors import ExpenseNotFoundError, CategoryNotFoundError, UnauthorizedOperationError


logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class UpdateExpenseResult:
    """Result of expense update operation."""
    expense_dto: ExpenseDTO
    events: list[DomainEvent]


class UpdateExpenseHandler:
    """Handler for expense update operations.
    
    This handler orchestrates the expense update use case by:
    1. Retrieving and validating the existing expense
    2. Checking user authorization
    3. Validating and applying updates
    4. Persisting changes through the repository
    5. Publishing domain events for downstream processing
    6. Returning updated expense DTO response
    """
    
    def __init__(
        self,
        expense_repository: ExpenseRepository,
        category_repository: CategoryRepository,
    ) -> None:
        """Initialize the update expense handler.
        
        Args:
            expense_repository: Repository for expense persistence operations.
            category_repository: Repository for category validation.
        """
        self._expense_repository = expense_repository
        self._category_repository = category_repository
    
    def handle(self, command: UpdateExpenseCommand) -> UpdateExpenseResult:
        """Execute the expense update use case.
        
        Args:
            command: The update command containing expense changes.
            
        Returns:
            UpdateExpenseResult containing updated expense DTO and domain events.
            
        Raises:
            ExpenseNotFoundError: If the expense doesn't exist.
            UnauthorizedOperationError: If user doesn't own the expense.
            CategoryNotFoundError: If specified category doesn't exist.
        """
        logger.info(f"Updating expense {command.expense_id} for user {command.user_id}")
        
        # Retrieve and validate existing expense
        existing = self._expense_repository.get_by_id(command.expense_id)
        if not existing:
            raise ExpenseNotFoundError(command.expense_id)
        
        # Check authorization
        user_id = UserId.from_string(command.user_id)
        if not existing.belongs_to_user(user_id):
            raise UnauthorizedOperationError("expense", command.expense_id, command.user_id)
        
        # Apply updates if provided
        if command.amount_tzs is not None:
            amount = AmountTZS.from_string(str(command.amount_tzs))
            existing.update_amount(amount)
            
        if command.description is not None:
            description = Description.from_string(command.description)
            existing.update_description(description)
            
        if command.date is not None:
            date = Date.from_string(command.date)
            existing.update_date(date)
            
        if command.category_id is not None:
            if command.category_id and not self._category_repository.exists_for_user(command.category_id, command.user_id):
                raise CategoryNotFoundError(command.category_id)
            category_id = CategoryId.from_string(command.category_id) if command.category_id else None
            existing.update_category(category_id)
        
        # Persist changes
        updated = self._expense_repository.update(existing)
        
        # Create domain event
        event = ExpenseUpdated(
            occurred_on=datetime.now(),
            expense_id=ExpenseId.from_string(existing.expense_id),
            user_id=existing.user_id,
            amount_tzs=float(existing.amount_tzs.value),
            description=str(existing.description.value),
            date=str(existing.date.value),
            category_id=existing.category_id
        )
        
        # Create DTO response
        dto = ExpenseDTO(
            expense_id=existing.expense_id,
            user_id=str(existing.user_id),
            amount_tzs=float(existing.amount_tzs.value),
            description=str(existing.description.value),
            date=str(existing.date.value),
            category_id=str(existing.category_id) if existing.category_id else None
        )
        
        logger.info(f"Updated expense {dto.expense_id}")
        return UpdateExpenseResult(expense_dto=dto, events=[event])