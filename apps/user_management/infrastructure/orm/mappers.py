"""Domain-ORM mappers for User Management.

This module contains mapper functions that convert between
domain entities/value objects and Django ORM models.
"""

from __future__ import annotations

from datetime import datetime
from typing import Dict, Any

from ...domain.entities.user import User
from ...domain.enums.user_status import UserStatus
from ...domain.value_objects.email import Email
from ...domain.value_objects.first_name import FirstName
from ...domain.value_objects.last_name import LastName
from ...domain.value_objects.password_hash import PasswordHash
from ...domain.value_objects.user_id import UserId
from .models import UserModel


def model_to_entity(model: UserModel) -> User:
    """Convert Django UserModel to User domain entity.
    
    Args:
        model: Django ORM model instance.
        
    Returns:
        User domain entity with all domain value objects.
        
    Raises:
        ValueError: If model data is invalid for domain entity creation.
    """
    try:
        return User(
            id=UserId(model.id),
            email=Email(model.email),
            password_hash=PasswordHash(model.password_hash),
            first_name=FirstName(model.first_name),
            last_name=LastName(model.last_name),
            status=UserStatus(model.status),
            created_at=model.created_at,
            updated_at=model.updated_at
        )
    except Exception as e:
        raise ValueError(f"Failed to convert UserModel to User entity: {e}") from e


def entity_to_model_data(entity: User) -> Dict[str, Any]:
    """Convert User domain entity to Django model data dictionary.
    
    Args:
        entity: User domain entity.
        
    Returns:
        Dictionary suitable for Django model creation/update.
        
    Note:
        Returns a dictionary rather than a model instance to support
        both create and update operations flexibly.
    """
    return {
        'id': entity.id.value,
        'email': entity.email.value,
        'password_hash': entity.password_hash.value,
        'first_name': entity.first_name.value,
        'last_name': entity.last_name.value,
        'status': entity.status.value,
        'created_at': entity.created_at,
        'updated_at': entity.updated_at,
    }


def create_model_from_entity(entity: User) -> UserModel:
    """Create a new Django UserModel from User domain entity.
    
    Args:
        entity: User domain entity.
        
    Returns:
        New UserModel instance (not saved to database).
        
    Note:
        The returned model is not saved. Call save() explicitly.
    """
    data = entity_to_model_data(entity)
    return UserModel(**data)


def update_model_from_entity(model: UserModel, entity: User) -> UserModel:
    """Update existing Django UserModel with User domain entity data.
    
    Args:
        model: Existing Django model instance.
        entity: User domain entity with updated data.
        
    Returns:
        Updated UserModel instance (not saved to database).
        
    Note:
        The returned model is not saved. Call save() explicitly.
    """
    data = entity_to_model_data(entity)
    
    # Update all fields except id (primary key should not change)
    for field, value in data.items():
        if field != 'id':
            setattr(model, field, value)
    
    return model


def validate_model_data(model: UserModel) -> None:
    """Validate that UserModel data can be converted to domain entity.
    
    Args:
        model: Django model instance to validate.
        
    Raises:
        ValueError: If model data is invalid for domain entity.
    """
    try:
        # Attempt to create domain value objects to validate data
        UserId(model.id)
        Email(model.email)
        PasswordHash(model.password_hash)
        FirstName(model.first_name)
        LastName(model.last_name)
        UserStatus(model.status)
    except Exception as e:
        raise ValueError(f"Invalid UserModel data for domain conversion: {e}") from e