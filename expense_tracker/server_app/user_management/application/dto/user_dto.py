"""User Data Transfer Object.

This module contains the DTO for user data representation
in the application layer responses.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Any


@dataclass(frozen=True, slots=True)
class UserDTO:
    """Data Transfer Object for User entity.
    
    This DTO provides a flat, presentation-ready representation
    of user data for API responses and inter-layer communication.
    
    Attributes:
        id: The user's unique identifier
        email: The user's email address
        first_name: The user's first name
        last_name: The user's last name
        full_name: The user's full name (computed)
        status: The user's current status
        created_at: When the user was created
        updated_at: When the user was last updated
    """
    
    id: str
    email: str
    first_name: str
    last_name: str
    full_name: str
    status: str
    created_at: datetime
    updated_at: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert DTO to dictionary representation.
        
        Returns:
            Dictionary representation of the user data.
        """
        return {
            'id': self.id,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'full_name': self.full_name,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> UserDTO:
        """Create DTO from dictionary representation.
        
        Args:
            data: Dictionary containing user data.
            
        Returns:
            UserDTO instance.
        """
        created_at = data['created_at']
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            
        updated_at = data['updated_at']
        if isinstance(updated_at, str):
            updated_at = datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
        
        return cls(
            id=data['id'],
            email=data['email'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            full_name=data['full_name'],
            status=data['status'],
            created_at=created_at,
            updated_at=updated_at
        )
    
    def __str__(self) -> str:
        """Return string representation."""
        return f"UserDTO(id={self.id}, email={self.email}, full_name={self.full_name})"
    
    def __repr__(self) -> str:
        """Return detailed string representation."""
        return (
            f"UserDTO(id='{self.id}', email='{self.email}', "
            f"first_name='{self.first_name}', last_name='{self.last_name}', "
            f"status='{self.status}')"
        )