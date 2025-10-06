"""Delete expense handler.

This module contains the handler for expense deletion use cases.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING, List

from ...domain.entities.expense import Expense
from ...domain.errors import ExpenseManagementDomainError
from ...domain.events.expense_events import DomainEvent
from ...domain.repositories.expense_repository import ExpenseRepository
from ...domain.value_objects.expense_id import ExpenseId
from ...domain.value_objects.user_id import UserId
from ..commands.delete_expense import DeleteExpenseCommand
from ..errors import translate_domain_error, ExpenseDeleteFailedError, ApplicationError

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class DeleteExpenseResult:
    """Result of expense deletion operation."""
    deleted_expense_id: str
    events: List[DomainEvent]


class DeleteExpenseHandler:
    """Handler for expense deletion operations.
    
    This handler orchestrates the expense deletion use case by:
    1. Validating the expense deletion request
    2. Finding and verifying ownership of the expense
    3. Deleting the expense through the repository
    4. Publishing domain events for downstream processing
    5. Returning a deletion confirmation response
    """
    
    def __init__(
        self,
        expense_repository: ExpenseRepository,
    ) -> None:
        """Initialize the delete expense handler.
        
        Args:
            expense_repository: Repository for expense persistence operations.
        """
        self._expense_repository = expense_repository
    
    def handle(self, command: DeleteExpenseCommand) -> DeleteExpenseResult:
        """Execute the expense deletion use case.
        
        Args:
            command: The deletion command containing expense identification data.
            
        Returns:
            DeleteExpenseResult containing deletion confirmation and domain events.
            
        Raises:
            ApplicationError: If expense deletion fails for any reason.
        """
        logger.info(f"Executing expense deletion for expense: {command.expense_id}")
        
        try:
            # Step 1: Validate the expense deletion request
            logger.debug(f"Validating expense deletion request for expense: {command.expense_id}")
            
            # Create domain value objects
            expense_id = ExpenseId.from_string(command.expense_id)
            user_id = UserId.from_string(command.user_id)
            
            # Step 2: Find the expense and verify ownership
            logger.debug(f"Finding expense {command.expense_id} and verifying ownership")
            expense = self._expense_repository.find_by_id(expense_id)
            if expense is None:
                logger.warning(f"Expense deletion failed: Expense {command.expense_id} not found")
                from ...domain.errors import ExpenseNotFoundError
                raise ExpenseNotFoundError(f"Expense {command.expense_id} not found")
            
            if expense.user_id != user_id:
                logger.warning(f"Expense deletion failed: User {command.user_id} does not own expense {command.expense_id}")
                from ...domain.errors import ExpenseAccessDeniedError
                raise ExpenseAccessDeniedError(f"User {command.user_id} does not own expense {command.expense_id}")
            
            # Step 3: Mark expense for deletion (generates domain event)
            logger.debug(f"Marking expense {command.expense_id} for deletion")
            expense.delete()
            
            # Step 4: Delete the expense from repository
            logger.debug(f"Deleting expense {expense.id} from repository")
            self._expense_repository.delete(expense_id)
            
            # Step 5: Collect domain events for publishing
            events = expense.get_domain_events()
            expense.clear_domain_events()
            logger.info(f"Expense deletion completed successfully for expense {command.expense_id}, collected {len(events)} domain events")
            
            return DeleteExpenseResult(
                deleted_expense_id=command.expense_id,
                events=events
            )
            
        except ExpenseManagementDomainError as e:
            logger.error(f"Domain error during expense deletion for expense {command.expense_id}: {str(e)}")
            raise translate_domain_error(e) from e
        except Exception as e:
            logger.error(f"Unexpected error during expense deletion for expense {command.expense_id}: {str(e)}")
            raise ExpenseDeleteFailedError(f"Failed to delete expense: {str(e)}") from e