"""Create expense handler.

This module contains the handler for expense creation use cases.
"""

from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Protocol

from ...domain.entities.expense import Expense
from ...domain.events.expense_events import DomainEvent, ExpenseCreated
from ...domain.repositories.expense_repository import ExpenseRepository
from ...domain.repositories.category_repository import CategoryRepository
from ...domain.value_objects.user.user_id import UserId
from ...domain.value_objects.expense.amount_tzs import AmountTZS
from ...domain.value_objects.expense.description import Description
from ...domain.value_objects.expense.date import Date
from ...domain.value_objects.category.category_id import CategoryId
from ...domain.value_objects.expense.expense_id import ExpenseId

from ..commands.expense_commands import CreateExpenseCommand
from ..dto.expense_dto import ExpenseDTO
from ..errors import ValidationError, CategoryNotFoundError


logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class CreateExpenseResult:
    """Result of expense creation operation."""
    expense_dto: ExpenseDTO
    events: list[DomainEvent]


class CreateExpenseHandler:
    """Handler for expense creation operations.
    
    This handler orchestrates the expense creation use case by:
    1. Validating the creation request
    2. Checking category existence if provided
    3. Creating a new expense domain entity
    4. Persisting the expense through the repository
    5. Publishing domain events for downstream processing
    6. Returning an expense DTO response
    """
    
    def __init__(
        self,
        expense_repository: ExpenseRepository,
        category_repository: CategoryRepository,
    ) -> None:
        """Initialize the create expense handler.
        
        Args:
            expense_repository: Repository for expense persistence operations.
            category_repository: Repository for category validation.
        """
        self._expense_repository = expense_repository
        self._category_repository = category_repository
    
    def handle(self, command: CreateExpenseCommand) -> CreateExpenseResult:
        """Execute the expense creation use case.
        
        Args:
            command: The creation command containing expense data.
            
        Returns:
            CreateExpenseResult containing expense DTO and domain events.
            
        Raises:
            ValidationError: If the expense data is invalid.
            CategoryNotFoundError: If the specified category doesn't exist.
        """
        logger.info(f"Creating expense for user: {command.user_id}")
        
        # Validate required fields
        if not command.description:
            raise ValidationError("description", "Description is required")
        
        # Create domain value objects
        user_id = UserId.from_string(command.user_id)
        amount = AmountTZS.from_string(str(command.amount_tzs))
        description = Description.from_string(command.description)
        date = Date.from_string(command.date)
        
        # Validate category if provided
        category_id = None
        if command.category_id:
            if not self._category_repository.exists_for_user(command.category_id, command.user_id):
                raise CategoryNotFoundError(command.category_id)
            category_id = CategoryId.from_string(command.category_id)
        # Create and persist the expense entity
        expense = Expense(
            expense_id=str(uuid.uuid4()),
            user_id=user_id,
            amount_tzs=amount,
            description=description,
            date=date,
            category_id=category_id
        )
        
        
        saved_expense = self._expense_repository.add(expense)
        # Create domain event
        event = ExpenseCreated(
            occurred_on=datetime.now(),
            expense_id=ExpenseId.from_string(expense.expense_id),
            user_id=expense.user_id,
            amount_tzs=float(expense.amount_tzs.value),
            description=str(expense.description.value),
            date=str(expense.date.value),
            category_id=expense.category_id
        )
        
        # Create DTO response
        dto = ExpenseDTO(
            expense_id=expense.expense_id,
            user_id=str(expense.user_id),
            amount_tzs=float(expense.amount_tzs.value),
            description=str(expense.description.value),
            date=str(expense.date.value),
            category_id=str(expense.category_id) if expense.category_id else None
        )
        
        logger.info(f"Created expense {dto.expense_id} for user {dto.user_id}")
        return CreateExpenseResult(expense_dto=dto, events=[event])