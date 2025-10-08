"""Update expense handler.

This module contains the handler for expense update use cases.
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
from ..commands.update_expense import UpdateExpenseCommand
from ..errors import translate_domain_error, ExpenseUpdateFailedError, ApplicationError
from ..dto import ExpenseDTO

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class UpdateExpenseResult:
    """Result of expense update operation."""
    expense_dto: ExpenseDTO
    events: List[DomainEvent]


class UpdateExpenseHandler:
    """Handler for expense update operations.
    
    This handler orchestrates the expense update use case by:
    1. Validating the expense update request
    2. Finding and verifying ownership of the expense
    3. Validating new category if provided
    4. Updating the expense domain entity
    5. Persisting the updated expense through the repository
    6. Publishing domain events for downstream processing
    7. Returning an updated expense DTO response
    """
    
    def __init__(
        self,
        expense_repository: ExpenseRepository,
        category_repository: CategoryRepository,
    ) -> None:
        """Initialize the update expense handler.
        
        Args:
            expense_repository: Repository for expense persistence operations.
            category_repository: Repository for category validation operations.
        """
        self._expense_repository = expense_repository
        self._category_repository = category_repository
    
    def handle(self, command: UpdateExpenseCommand) -> UpdateExpenseResult:
        """Execute the expense update use case.
        
        Args:
            command: The update command containing expense data.
            
        Returns:
            UpdateExpenseResult containing updated expense DTO and domain events.
            
        Raises:
            ApplicationError: If expense update fails for any reason.
        """
        logger.info(f"Executing expense update for expense: {command.expense_id}")
        
        try:
            # Step 1: Validate the expense update request
            logger.debug(f"Validating expense update request for expense: {command.expense_id}")
            
            if not command.has_updates():
                logger.warning(f"Expense update failed: No update data provided for expense {command.expense_id}")
                raise ApplicationError("No update data provided")
            
            # Create domain value objects
            expense_id = ExpenseId.from_string(command.expense_id)
            user_id = UserId.from_string(command.user_id)
            
            # Step 2: Find the expense and verify ownership
            logger.debug(f"Finding expense {command.expense_id} and verifying ownership")
            expense = self._expense_repository.find_by_id(expense_id)
            if expense is None:
                logger.warning(f"Expense update failed: Expense {command.expense_id} not found")
                from ...domain.errors import ExpenseNotFoundError
                raise ExpenseNotFoundError(f"Expense {command.expense_id} not found")
            
            if expense.user_id != user_id:
                logger.warning(f"Expense update failed: User {command.user_id} does not own expense {command.expense_id}")
                from ...domain.errors import ExpenseAccessDeniedError
                raise ExpenseAccessDeniedError(f"User {command.user_id} does not own expense {command.expense_id}")
            
            # Step 3: Validate new category if provided
            new_category_id = None
            if command.category_id:
                logger.debug(f"Validating new category {command.category_id} for expense update")
                new_category_id = CategoryId.from_string(command.category_id)
                category = self._category_repository.find_by_id(new_category_id)
                if category is None:
                    logger.warning(f"Expense update failed: Category {command.category_id} not found")
                    from ...domain.errors import CategoryNotFoundError
                    raise CategoryNotFoundError(f"Category {command.category_id} not found")
                
                if category.user_id != user_id:
                    logger.warning(f"Expense update failed: Category {command.category_id} does not belong to user {command.user_id}")
                    from ...domain.errors import CategoryAccessDeniedError
                    raise CategoryAccessDeniedError(f"Category {command.category_id} does not belong to user {command.user_id}")
            
            # Step 4: Prepare update values
            logger.debug(f"Preparing update values for expense {command.expense_id}")
            new_amount_tzs = AmountTZS.from_float(command.amount_tzs) if command.amount_tzs is not None else None
            new_description = ExpenseDescription.from_string(command.description) if command.description is not None else None
            
            # Step 5: Update the expense entity
            logger.debug(f"Updating expense {command.expense_id} with new values")
            expense.update(
                amount_tzs=new_amount_tzs,
                description=new_description,
                category_id=new_category_id,
                expense_date=command.expense_date
            )
            
            # Step 6: Persist the updated expense
            logger.debug(f"Persisting updated expense {expense.expense_id} to repository")
            self._expense_repository.update(expense)
            
            # Step 7: Create expense DTO for response
            logger.debug(f"Creating expense DTO for successful update of expense {command.expense_id}")
            expense_dto = ExpenseDTO(
                id=str(expense.expense_id.value),
                user_id=str(expense.user_id.value),
                category_id=str(expense.category_id.value),
                amount_tzs=expense.amount_tzs.value,
                description=expense.description.value if expense.description else None,
                expense_date=expense.expense_date,
                created_at=expense.created_at,
                updated_at=expense.updated_at
            )
            
            # Step 8: Collect domain events for publishing
            events = expense.clear_events()
            logger.info(f"Expense update completed successfully for expense {command.expense_id}, collected {len(events)} domain events")
            
            return UpdateExpenseResult(
                expense_dto=expense_dto,
                events=events
            )
            
        except ExpenseManagementDomainError as e:
            logger.error(f"Domain error during expense update for expense {command.expense_id}: {str(e)}")
            raise translate_domain_error(e) from e
        except Exception as e:
            logger.error(f"Unexpected error during expense update for expense {command.expense_id}: {str(e)}")
            raise ExpenseUpdateFailedError(f"Failed to update expense: {str(e)}") from e