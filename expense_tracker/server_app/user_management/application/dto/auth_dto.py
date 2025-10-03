"""Authentication Result Data Transfer Object.

This module contains the DTO for authentication operation results.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Any

from .user_dto import UserDTO


@dataclass(frozen=True, slots=True)
class AuthResultDTO:
    """Data Transfer Object for authentication results.
    
    This DTO provides the result of authentication operations,
    including the JWT token and user information.
    
    Attributes:
        token: The JWT authentication token
        user: The authenticated user's data
    """
    
    token: str
    user: UserDTO
    
    
    
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert DTO to dictionary representation.
        
        Returns:
            Dictionary representation of the authentication result.
        """
        return {
            'token': self.token,
            'user': self.user.to_dict()
        }
    
    
    
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> AuthResultDTO:
        """Create DTO from dictionary representation.
        
        Args:
            data: Dictionary containing authentication result data.
            
        Returns:
            AuthResultDTO instance.
        """
        return cls(
            token=data['token'],
            user=UserDTO.from_dict(data['user'])
        )
    
    def __str__(self) -> str:
        """Return string representation."""
        return f"AuthResultDTO(user={self.user.email}, token_length={len(self.token)})"
    
    def __repr__(self) -> str:
        """Return detailed string representation."""
        return (
            f"AuthResultDTO(token='***', "
            f"user={self.user!r})"
        )