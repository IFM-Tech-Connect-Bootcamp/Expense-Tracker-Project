"""Delete category handler.

This module contains the handler for category deletion use cases.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING, List

from ...domain.entities.category import Category
from ...domain.errors import ExpenseManagementDomainError
from ...domain.events.category_events import DomainEvent
from ...domain.repositories.category_repository import CategoryRepository
from ...domain.repositories.expense_repository import ExpenseRepository
from ...domain.value_objects.category_id import CategoryId
from ...domain.value_objects.user_id import UserId
from ..commands.delete_category import DeleteCategoryCommand
from ..errors import translate_domain_error, CategoryDeleteFailedError, ApplicationError

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class DeleteCategoryResult:
    """Result of category deletion operation."""
    deleted_category_id: str
    events: List[DomainEvent]


class DeleteCategoryHandler:
    """Handler for category deletion operations.
    
    This handler orchestrates the category deletion use case by:
    1. Validating the category deletion request
    2. Finding and verifying ownership of the category
    3. Checking that the category is not in use by expenses
    4. Deleting the category through the repository
    5. Publishing domain events for downstream processing
    6. Returning a deletion confirmation response
    """
    
    def __init__(
        self,
        category_repository: CategoryRepository,
        expense_repository: ExpenseRepository,
    ) -> None:
        """Initialize the delete category handler.
        
        Args:
            category_repository: Repository for category persistence operations.
            expense_repository: Repository for expense validation operations.
        """
        self._category_repository = category_repository
        self._expense_repository = expense_repository
    
    def handle(self, command: DeleteCategoryCommand) -> DeleteCategoryResult:
        """Execute the category deletion use case.
        
        Args:
            command: The deletion command containing category identification data.
            
        Returns:
            DeleteCategoryResult containing deletion confirmation and domain events.
            
        Raises:
            ApplicationError: If category deletion fails for any reason.
        """
        logger.info(f"Executing category deletion for category: {command.category_id}")
        
        try:
            # Step 1: Validate the category deletion request
            logger.debug(f"Validating category deletion request for category: {command.category_id}")
            
            # Create domain value objects
            category_id = CategoryId.from_string(command.category_id)
            user_id = UserId.from_string(command.user_id)
            
            # Step 2: Find the category and verify ownership
            logger.debug(f"Finding category {command.category_id} and verifying ownership")
            category = self._category_repository.find_by_id(category_id)
            if category is None:
                logger.warning(f"Category deletion failed: Category {command.category_id} not found")
                from ...domain.errors import CategoryNotFoundError
                raise CategoryNotFoundError(f"Category {command.category_id} not found")
            
            if category.user_id != user_id:
                logger.warning(f"Category deletion failed: User {command.user_id} does not own category {command.category_id}")
                from ...domain.errors import CategoryAccessDeniedError
                raise CategoryAccessDeniedError(f"User {command.user_id} does not own category {command.category_id}")
            
            # Step 3: Check that category is not in use by expenses
            logger.debug(f"Checking if category {command.category_id} is in use by expenses")
            expense_count = self._expense_repository.count_by_category_id(category_id)
            if expense_count > 0:
                logger.warning(f"Category deletion failed: Category {command.category_id} is in use by {expense_count} expenses")
                from ...domain.errors import CategoryInUseError
                raise CategoryInUseError(f"Category {command.category_id} is in use by {expense_count} expenses")
            
            # Step 4: Mark category for deletion (generates domain event)
            logger.debug(f"Marking category {command.category_id} for deletion")
            category.delete()
            
            # Step 5: Delete the category from repository
            logger.debug(f"Deleting category {category.id} from repository")
            self._category_repository.delete(category_id)
            
            # Step 6: Collect domain events for publishing
            events = category.get_domain_events()
            category.clear_domain_events()
            logger.info(f"Category deletion completed successfully for category {command.category_id}, collected {len(events)} domain events")
            
            return DeleteCategoryResult(
                deleted_category_id=command.category_id,
                events=events
            )
            
        except ExpenseManagementDomainError as e:
            logger.error(f"Domain error during category deletion for category {command.category_id}: {str(e)}")
            raise translate_domain_error(e) from e
        except Exception as e:
            logger.error(f"Unexpected error during category deletion for category {command.category_id}: {str(e)}")
            raise CategoryDeleteFailedError(f"Failed to delete category: {str(e)}") from e