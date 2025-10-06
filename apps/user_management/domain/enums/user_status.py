"""User status enumeration."""

from enum import Enum, unique
from typing import Self


@unique
class UserStatus(Enum):
    """Enumeration of possible user status values.
    
    This enum defines the lifecycle states a user can be in within the system.
    """
    
    ACTIVE = "active"
    DEACTIVATED = "deactivated"
    
    
    
    
    def __str__(self) -> str:
        """Return the string value of the status."""
        return self.value
    
    
    
    
    def __repr__(self) -> str:
        """Return a detailed string representation."""
        return f"UserStatus.{self.name}"
    
    
    
    
    @classmethod
    def from_string(cls, value: str) -> Self:
        """Create a UserStatus from a string value.
        
        Args:
            value: The string representation of the status.
            
        Returns:
            UserStatus instance.
            
        Raises:
            ValueError: If the string doesn't match any status.
        """
        try:
            return cls(value.lower().strip())
        except ValueError as e:
            valid_values = [status.value for status in cls]
            raise ValueError(
                f"Invalid user status: {value}. Valid values are: {valid_values}"
            ) from e
    
    
    
    
    @property
    def is_active(self) -> bool:
        """Check if the status represents an active user.
        
        Returns:
            True if the user is active, False otherwise.
        """
        return self == UserStatus.ACTIVE
    
    
    
    
    
    @property
    def is_deactivated(self) -> bool:
        """Check if the status represents a deactivated user.
        
        Returns:
            True if the user is deactivated, False otherwise.
        """
        return self == UserStatus.DEACTIVATED