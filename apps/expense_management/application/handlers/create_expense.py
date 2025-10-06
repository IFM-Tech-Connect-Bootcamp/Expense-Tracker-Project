"""Create expense handler.

This module contains the handler for expense creation use cases.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING, List

from ...domain.entities.expense import Expense
from ...domain.errors import ExpenseManagementDomainError
from ...domain.events.expense_events import DomainEvent
from ...domain.repositories.expense_repository import ExpenseRepository
from ...domain.repositories.category_repository import CategoryRepository
from ...domain.value_objects.expense_id import ExpenseId
from ...domain.value_objects.category_id import CategoryId
from ...domain.value_objects.user_id import UserId
from ...domain.value_objects.amount_tzs import AmountTZS
from ...domain.value_objects.expense_description import ExpenseDescription
from ..commands.create_expense import CreateExpenseCommand
from ..errors import translate_domain_error, ExpenseCreationFailedError, ApplicationError
from ..dto import ExpenseDTO

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class CreateExpenseResult:
    """Result of expense creation operation."""
    expense_dto: ExpenseDTO
    events: List[DomainEvent]


class CreateExpenseHandler:
    """Handler for expense creation operations.
    
    This handler orchestrates the expense creation use case by:
    1. Validating the expense creation request
    2. Checking that the category exists and belongs to the user
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
            category_repository: Repository for category validation operations.
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
            ApplicationError: If expense creation fails for any reason.
        """
        logger.info(f"Executing expense creation for user: {command.user_id}")
        
        try:
            # Step 1: Validate the expense creation request
            logger.debug(f"Validating expense creation request for user: {command.user_id}")
            
            # Create domain value objects
            user_id = UserId.from_string(command.user_id)
            category_id = CategoryId.from_string(command.category_id)
            amount_tzs = AmountTZS.from_float(command.amount_tzs)
            description = ExpenseDescription.from_string(command.description) if command.description else None
            
            # Step 2: Validate that category exists and belongs to user
            logger.debug(f"Validating category {command.category_id} belongs to user {command.user_id}")
            category = self._category_repository.find_by_id(category_id)
            if category is None:
                logger.warning(f"Expense creation failed: Category {command.category_id} not found")
                from ...domain.errors import CategoryNotFoundError
                raise CategoryNotFoundError(f"Category {command.category_id} not found")
            
            if category.user_id != user_id:
                logger.warning(f"Expense creation failed: Category {command.category_id} does not belong to user {command.user_id}")
                from ...domain.errors import CategoryAccessDeniedError
                raise CategoryAccessDeniedError(f"Category {command.category_id} does not belong to user {command.user_id}")
            
            # Step 3: Create new expense domain entity
            logger.debug(f"Creating new expense entity for user {command.user_id}")
            expense = Expense.create(
                user_id=user_id,
                category_id=category_id,
                amount_tzs=amount_tzs,
                description=description,
                expense_date=command.expense_date,
                expense_id=ExpenseId.new()
            )
            
            # Step 4: Persist the expense
            logger.debug(f"Persisting expense {expense.id} to repository")
            self._expense_repository.save(expense)
            
            # Step 5: Create expense DTO for response
            logger.debug(f"Creating expense DTO for successful creation by user {command.user_id}")
            expense_dto = ExpenseDTO(
                id=str(expense.id.value),
                user_id=str(expense.user_id.value),
                category_id=str(expense.category_id.value),
                amount_tzs=expense.amount_tzs.value,
                description=expense.description.value if expense.description else None,
                expense_date=expense.expense_date,
                created_at=expense.created_at,
                updated_at=expense.updated_at
            )
            
            # Step 6: Collect domain events for publishing
            events = expense.get_domain_events()
            expense.clear_domain_events()
            logger.info(f"Expense creation completed successfully for user {command.user_id}, collected {len(events)} domain events")
            
            return CreateExpenseResult(
                expense_dto=expense_dto,
                events=events
            )
            
        except ExpenseManagementDomainError as e:
            logger.error(f"Domain error during expense creation for user {command.user_id}: {str(e)}")
            raise translate_domain_error(e) from e
        except Exception as e:
            logger.error(f"Unexpected error during expense creation for user {command.user_id}: {str(e)}")
            raise ExpenseCreationFailedError(f"Failed to create expense: {str(e)}") from e