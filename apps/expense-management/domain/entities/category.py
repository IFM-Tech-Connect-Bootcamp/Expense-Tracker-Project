from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, TYPE_CHECKING
from django.utils import timezone

from ..value_objects.user.user_id import UserId
from ..value_objects.category.category_id import CategoryId
from ..value_objects.category.name import CategoryName

"""
from ..errors import (
    InvalidOperationError,
    DomainValidationError,
    PasswordPolicyError
)
"""
"""
if TYPE_CHECKING:
    from ..services.password_policy import PasswordHasher
    from ..events.user_events import DomainEvent
"""

@dataclass
class Category:
    """Represents an category entity with various attributes and validation."""
    
    category_id: CategoryId
    user_id: UserId
    name: CategoryName
    created_at: datetime = field(default_factory=timezone.now)
    updated_at: datetime = field(default_factory=timezone.now)
    
    def update_name(self, new_name: CategoryName) -> None:
        """Update the name of the category."""
        self.name = new_name
        self.updated_at = timezone.now()
    
    