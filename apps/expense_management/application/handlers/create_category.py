"""Create category handler.

This module contains the handler for category creation use cases.
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
from ..commands.create_category import CreateCategoryCommand
from ..errors import translate_domain_error, CategoryCreationFailedError, ApplicationError
from ..dto import CategoryDTO

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class CreateCategoryResult:
    """Result of category creation operation."""
    category_dto: CategoryDTO
    events: List[DomainEvent]


class CreateCategoryHandler:
    """Handler for category creation operations.
    
    This handler orchestrates the category creation use case by:
    1. Validating the category creation request
    2. Checking for category name uniqueness per user
    3. Creating a new category domain entity
    4. Persisting the category through the repository
    5. Publishing domain events for downstream processing
    6. Returning a category DTO response
    """
    
    def __init__(
        self,
        category_repository: CategoryRepository,
    ) -> None:
        """Initialize the create category handler.
        
        Args:
            category_repository: Repository for category persistence operations.
        """
        self._category_repository = category_repository
    
    def handle(self, command: CreateCategoryCommand) -> CreateCategoryResult:
        """Execute the category creation use case.
        
        Args:
            command: The creation command containing category data.
            
        Returns:
            CreateCategoryResult containing category DTO and domain events.
            
        Raises:
            ApplicationError: If category creation fails for any reason.
        """
        logger.info(f"Executing category creation for user: {command.user_id}")
        
        try:
            # Step 1: Validate the category creation request
            logger.debug(f"Validating category creation request for user: {command.user_id}")
            
            # Create domain value objects
            user_id = UserId.from_string(command.user_id)
            category_name = CategoryName.from_string(command.name)
            
            # Step 2: Check for category name uniqueness per user
            logger.debug(f"Checking category name uniqueness for user {command.user_id}: {command.name}")
            existing_categories = self._category_repository.find_by_user_id(user_id)
            
            CategoryValidationService.validate_category_name_unique_for_user(
                existing_categories, user_id, command.name
            )
            
            # Step 3: Create new category domain entity
            logger.debug(f"Creating new category entity for user {command.user_id}")
            category = Category.create(
                user_id=user_id,
                name=category_name
            )
            
            # Step 4: Persist the category
            logger.debug(f"Persisting category {category.category_id} to repository")
            self._category_repository.save(category)
            
            # Step 5: Create category DTO for response
            logger.debug(f"Creating category DTO for successful creation by user {command.user_id}")
            category_dto = CategoryDTO(
                id=str(category.category_id.value),
                user_id=str(category.user_id.value),
                name=category.name.value,
                created_at=category.created_at,
                updated_at=category.updated_at
            )
            
            # Step 6: Collect domain events for publishing
            events = category.clear_events()
            logger.info(f"Category creation completed successfully for user {command.user_id}, collected {len(events)} domain events")
            
            return CreateCategoryResult(
                category_dto=category_dto,
                events=events
            )
            
        except ExpenseManagementDomainError as e:
            logger.error(f"Domain error during category creation for user {command.user_id}: {str(e)}")
            raise translate_domain_error(e) from e
        except Exception as e:
            logger.error(f"Unexpected error during category creation for user {command.user_id}: {str(e)}")
            raise CategoryCreationFailedError(f"Failed to create category: {str(e)}") from e