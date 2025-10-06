"""Django implementation of UserRepository.

This module provides a concrete implementation of the UserRepository
interface using Django ORM for persistence.
"""

from __future__ import annotations

import logging
from typing import Optional

from django.db import IntegrityError, transaction
from django.core.exceptions import ObjectDoesNotExist

from ...domain.entities.user import User
from ...domain.errors import UserAlreadyExistsError, UserNotFoundError
from ...domain.repositories.user_repository import UserRepository
from ...domain.value_objects.email import Email
from ...domain.value_objects.user_id import UserId
from ..orm.mappers import (
    create_model_from_entity,
    entity_to_model_data,
    model_to_entity,
    update_model_from_entity,
    validate_model_data,
)
from ..orm.models import UserModel

logger = logging.getLogger(__name__)


class DjangoUserRepository(UserRepository):
    """Django ORM implementation of UserRepository.
    
    Provides persistence operations for User entities using Django ORM.
    Handles mapping between domain entities and database models.
    Translates database errors to domain errors.
    """

    def find_by_id(self, user_id: UserId) -> Optional[User]:
        """Find user by ID.
        
        Args:
            user_id: Unique user identifier.
            
        Returns:
            User entity if found, None otherwise.
            
        Raises:
            ValueError: If database data is invalid for domain entity.
        """
        logger.debug(f"Finding user by ID: {user_id.value}")
        
        try:
            model = UserModel.objects.get(id=user_id.value)
            validate_model_data(model)
            user = model_to_entity(model)
            logger.debug(f"Found user: {user.id.value}")
            return user
        except ObjectDoesNotExist:
            logger.debug(f"User not found: {user_id.value}")
            return None
        except Exception as e:
            logger.error(f"Error finding user by ID {user_id.value}: {e}")
            raise ValueError(f"Failed to find user: {e}") from e

    def find_by_email(self, email: Email) -> Optional[User]:
        """Find user by email address.
        
        Args:
            email: Email to search for.
            
        Returns:
            User entity if found, None otherwise.
            
        Raises:
            ValueError: If database data is invalid for domain entity.
        """
        logger.debug(f"Finding user by email: {email.value}")
        
        try:
            model = UserModel.objects.filter(email=email.value).first()
            if model:
                user = model_to_entity(model)
                logger.debug(f"Found user: {user.id.value}")
                return user
            
            logger.debug(f"No user found with email: {email.value}")
            return None
            
        except Exception as e:
            logger.error(f"Error finding user by email {email.value}: {e}")
            raise

    def find_active_by_email(self, email: Email) -> Optional[User]:
        """Find active user by email address.
        
        Args:
            email: Email to search for.
            
        Returns:
            Active user entity if found, None otherwise.
            
        Raises:
            ValueError: If database data is invalid for domain entity.
        """
        logger.debug(f"Finding active user by email: {email.value}")
        
        try:
            model = UserModel.objects.filter(
                email=email.value, 
                status="active"
            ).first()
            if model:
                user = model_to_entity(model)
                logger.debug(f"Found active user: {user.id.value}")
                return user
            
            logger.debug(f"No active user found with email: {email.value}")
            return None
            
        except Exception as e:
            logger.error(f"Error finding active user by email {email.value}: {e}")
            raise

    def exists_by_email(self, email: Email) -> bool:
        """Check if user exists by email address.
        
        Args:
            email: User's email address.
            
        Returns:
            True if user exists, False otherwise.
        """
        logger.debug(f"Checking if user exists by email: {email.value}")
        
        try:
            exists = UserModel.objects.filter(email=email.value).exists()
            logger.debug(f"User exists: {exists}")
            return exists
        except Exception as e:
            logger.error(f"Error checking user existence by email {email.value}: {e}")
            raise ValueError(f"Failed to check user existence: {e}") from e

    def save(self, user: User) -> User:
        """Save new user to database.
        
        Args:
            user: User entity to save.
            
        Returns:
            Saved user entity with any generated fields.
            
        Raises:
            UserAlreadyExistsError: If user with same email already exists.
            ValueError: If user data is invalid.
        """
        logger.debug(f"Saving new user: {user.email.value}")
        
        try:
            # Check if user already exists
            if self.exists_by_email(user.email):
                raise UserAlreadyExistsError(f"User with email {user.email.value} already exists")
            
            # Create new model
            model_data = entity_to_model_data(user)
            
            model = UserModel.objects.create(**model_data)
            logger.info(f"User saved with ID: {model.id}")
            
            # Convert back to entity and return
            saved_user = model_to_entity(model)
            return saved_user
                
        except IntegrityError as e:
            logger.error(f"Database integrity error saving user: {e}")
            if "email" in str(e).lower():
                raise UserAlreadyExistsError(f"User with email {user.email.value} already exists")
            raise ValueError(f"Invalid user data: {e}")
        except Exception as e:
            logger.error(f"Error saving user {user.email.value}: {e}")
            raise

    def update(self, user: User) -> User:
        """Update existing user entity in database.
        
        Args:
            user: User entity to update.
            
        Returns:
            Updated user entity.
            
        Raises:
            UserNotFoundError: If user doesn't exist.
            UserAlreadyExistsError: If email change conflicts with existing user.
            ValueError: If update operation fails.
        """
        logger.debug(f"Updating user: {user.id.value}")
        
        try:
            # Get existing model
            try:
                existing_model = UserModel.objects.get(id=user.id.value)
            except ObjectDoesNotExist:
                logger.warning(f"User not found for update: {user.id.value}")
                raise UserNotFoundError(str(user.id.value))
            
            # Update model with new data
            try:
                updated_model = update_model_from_entity(existing_model, user)
                updated_model.save()
            except IntegrityError as e:
                if 'email' in str(e).lower():
                    logger.warning(f"Email already exists during update: {user.email.value}")
                    raise UserAlreadyExistsError(user.email.value) from e
                raise ValueError(f"Database integrity error: {e}") from e
            
            # Return updated entity
            validate_model_data(updated_model)
            updated_user = model_to_entity(updated_model)
                
            logger.info(f"Successfully updated user: {user.id.value}")
            return updated_user
            
        except (UserNotFoundError, UserAlreadyExistsError):
            raise
        except Exception as e:
            logger.error(f"Error updating user {user.id.value}: {e}")
            raise ValueError(f"Failed to update user: {e}") from e

    def delete(self, user_id: UserId) -> None:
        """Delete user from database.
        
        Args:
            user_id: ID of user to delete.
            
        Raises:
            UserNotFoundError: If user doesn't exist.
            ValueError: If delete operation fails.
        """
        logger.debug(f"Deleting user: {user_id.value}")
        
        try:
            try:
                model = UserModel.objects.get(id=user_id.value)
                model.delete()
            except ObjectDoesNotExist:
                logger.warning(f"User not found for deletion: {user_id.value}")
                raise UserNotFoundError(str(user_id.value))
            
            logger.info(f"Successfully deleted user: {user_id.value}")
            
        except UserNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Error deleting user {user_id.value}: {e}")
            raise ValueError(f"Failed to delete user: {e}") from e

    def find_active_users(self, limit: int = 100, offset: int = 0) -> list[User]:
        """Find active users with pagination.
        
        Args:
            limit: Maximum number of users to return.
            offset: Number of users to skip.
            
        Returns:
            List of active user entities.
            
        Raises:
            ValueError: If query fails or data is invalid.
        """
        logger.debug(f"Finding active users (limit={limit}, offset={offset})")
        
        try:
            models = UserModel.objects.filter(status='active')[offset:offset + limit]
            users = []
            
            for model in models:
                validate_model_data(model)
                user = model_to_entity(model)
                users.append(user)
            
            logger.debug(f"Found {len(users)} active users")
            return users
            
        except Exception as e:
            logger.error(f"Error finding active users: {e}")
            raise ValueError(f"Failed to find active users: {e}") from e

    def count_active_users(self) -> int:
        """Count active users in the system.
        
        Returns:
            Number of active users.
            
        Raises:
            ValueError: If there's an error accessing the database.
        """
        logger.debug("Counting active users")
        
        try:
            count = UserModel.objects.filter(status="active").count()
            logger.debug(f"Found {count} active users")
            return count
            
        except Exception as e:
            logger.error(f"Error counting active users: {e}")
            raise ValueError(f"Database error: {e}")

    def count_users(self) -> int:
        """Count all users in the system.
        
        Returns:
            Total number of users.
            
        Raises:
            ValueError: If there's an error accessing the database.
        """
        logger.debug("Counting all users")
        
        try:
            count = UserModel.objects.count()
            logger.debug(f"Found {count} total users")
            return count
            
        except Exception as e:
            logger.error(f"Error counting users: {e}")
            raise ValueError(f"Database error: {e}")