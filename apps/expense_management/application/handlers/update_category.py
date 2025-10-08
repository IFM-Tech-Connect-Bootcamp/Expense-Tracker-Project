"""Update category handler.

This module contains the handler for category update use cases.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING, List

from ...domain.entities.category import Category
from ...domain.errors import ExpenseManagementDomainError
from ...domain.events.category_events import DomainEvent
from ...domain.repositories.category_repository import CategoryRepository
from ...domain.value_objects.category_id import CategoryId
from ...domain.value_objects.user_id import UserId
from ...domain.value_objects.category_name import CategoryName
from ...domain.services.category_validation_service import CategoryValidationService
from ..commands.update_category import UpdateCategoryCommand
from ..errors import translate_domain_error, CategoryUpdateFailedError, ApplicationError
from ..dto import CategoryDTO

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class UpdateCategoryResult:
    """Result of category update operation."""
    category_dto: CategoryDTO
    events: List[DomainEvent]


class UpdateCategoryHandler:
    """Handler for category update operations.
    
    This handler orchestrates the category update use case by:
    1. Validating the category update request
    2. Finding and verifying ownership of the category
    3. Checking for category name uniqueness per user
    4. Updating the category domain entity
    5. Persisting the updated category through the repository
    6. Publishing domain events for downstream processing
    7. Returning an updated category DTO response
    """
    
    def __init__(
        self,
        category_repository: CategoryRepository,
    ) -> None:
        """Initialize the update category handler.
        
        Args:
            category_repository: Repository for category persistence operations.
        """
        self._category_repository = category_repository
    
    def handle(self, command: UpdateCategoryCommand) -> UpdateCategoryResult:
        """Execute the category update use case.
        
        Args:
            command: The update command containing category data.
            
        Returns:
            UpdateCategoryResult containing updated category DTO and domain events.
            
        Raises:
            ApplicationError: If category update fails for any reason.
        """
        logger.info(f"Executing category update for category: {command.category_id}")
        
        try:
            # Step 1: Validate the category update request
            logger.debug(f"Validating category update request for category: {command.category_id}")
            
            # Create domain value objects
            category_id = CategoryId.from_string(command.category_id)
            user_id = UserId.from_string(command.user_id)
            new_category_name = CategoryName.from_string(command.name)
            
            # Step 2: Find the category and verify ownership
            logger.debug(f"Finding category {command.category_id} and verifying ownership")
            category = self._category_repository.find_by_id(category_id)
            if category is None:
                logger.warning(f"Category update failed: Category {command.category_id} not found")
                from ...domain.errors import CategoryNotFoundError
                raise CategoryNotFoundError(f"Category {command.category_id} not found")
            
            if category.user_id != user_id:
                logger.warning(f"Category update failed: User {command.user_id} does not own category {command.category_id}")
                from ...domain.errors import CategoryAccessDeniedError
                raise CategoryAccessDeniedError(f"User {command.user_id} does not own category {command.category_id}")
            
            # Step 3: Check for category name uniqueness per user (if name is changing)
            if category.name.value != new_category_name.value:
                logger.debug(f"Checking category name uniqueness for user {command.user_id}: {command.name}")
                existing_categories = self._category_repository.find_by_user_id(user_id)
                
                CategoryValidationService.validate_category_name_unique_for_user(
                    existing_categories, user_id, command.name, exclude_category_id=category_id
                )
            
            # Step 4: Update the category entity
            logger.debug(f"Updating category {command.category_id} with new name: {command.name}")
            category.rename(new_category_name)
            
            # Step 5: Persist the updated category
            logger.debug(f"Persisting updated category {category.category_id} to repository")
            self._category_repository.update(category)
            
            # Step 6: Create category DTO for response
            logger.debug(f"Creating category DTO for successful update of category {command.category_id}")
            category_dto = CategoryDTO(
                id=str(category.category_id.value),
                user_id=str(category.user_id.value),
                name=category.name.value,
                created_at=category.created_at,
                updated_at=category.updated_at
            )
            
            # Step 7: Collect domain events for publishing
            events = category.clear_events()
            logger.info(f"Category update completed successfully for category {command.category_id}, collected {len(events)} domain events")
            
            return UpdateCategoryResult(
                category_dto=category_dto,
                events=events
            )
            
        except ExpenseManagementDomainError as e:
            logger.error(f"Domain error during category update for category {command.category_id}: {str(e)}")
            raise translate_domain_error(e) from e
        except Exception as e:
            logger.error(f"Unexpected error during category update for category {command.category_id}: {str(e)}")
            raise CategoryUpdateFailedError(f"Failed to update category: {str(e)}") from e