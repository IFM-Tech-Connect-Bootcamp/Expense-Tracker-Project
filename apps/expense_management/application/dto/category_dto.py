"""Category Data Transfer Object.

This module contains the DTO for category data representation
in the application layer responses.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Any


@dataclass(frozen=True, slots=True)
class CategoryDTO:
    """Data Transfer Object for Category entity.
    
    This DTO provides a flat, presentation-ready representation
    of category data for API responses and inter-layer communication.
    
    Attributes:
        id: The category's unique identifier
        user_id: The ID of the user who owns this category
        name: The name of the category
        created_at: When the category was created
        updated_at: When the category was last updated
    """
    
    id: str
    user_id: str
    name: str
    created_at: datetime
    updated_at: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert DTO to dictionary representation.
        
        Returns:
            Dictionary representation of the category data.
        """
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> CategoryDTO:
        """Create DTO from dictionary representation.
        
        Args:
            data: Dictionary containing category data.
            
        Returns:
            CategoryDTO instance.
        """
        created_at = data['created_at']
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            
        updated_at = data['updated_at']
        if isinstance(updated_at, str):
            updated_at = datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
        
        return cls(
            id=data['id'],
            user_id=data['user_id'],
            name=data['name'],
            created_at=created_at,
            updated_at=updated_at
        )
    
    def __str__(self) -> str:
        """Return string representation."""
        return f"CategoryDTO(id={self.id}, name={self.name})"
    
    def __repr__(self) -> str:
        """Return detailed string representation."""
        return (
            f"CategoryDTO(id='{self.id}', user_id='{self.user_id}', "
            f"name='{self.name}')"
        )