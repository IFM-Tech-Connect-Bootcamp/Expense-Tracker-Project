"""Authentication Result Data Transfer Object.

This module contains the DTO for authentication operation results.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Any, Optional

from .user_dto import UserDTO


@dataclass(frozen=True, slots=True)
class AuthResultDTO:
    """Data Transfer Object for authentication results.
    
    This DTO provides the result of authentication operations,
    including the access token and user information.
    
    Attributes:
        user: The authenticated user's data
        access_token: The JWT authentication token
        token_type: The type of token (default: "Bearer")
        expires_in: Token expiration time in seconds
    """
    
    user: UserDTO
    access_token: str
    token_type: str = "Bearer"
    expires_in: Optional[int] = None
    
    
    
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert DTO to dictionary representation.
        
        Returns:
            Dictionary representation of the authentication result.
        """
        return {
            'user': self.user.to_dict(),
            'access_token': self.access_token,
            'token_type': self.token_type,
            'expires_in': self.expires_in
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
            user=UserDTO.from_dict(data['user']),
            access_token=data['access_token'],
            token_type=data.get('token_type', 'Bearer'),
            expires_in=data.get('expires_in')
        )
    
    def __str__(self) -> str:
        """Return string representation."""
        return f"AuthResultDTO(user={self.user.email}, token_length={len(self.access_token)})"
    
    def __repr__(self) -> str:
        """Return detailed string representation."""
        return (
            f"AuthResultDTO(access_token='***', token_type='{self.token_type}', "
            f"expires_in={self.expires_in}, user={self.user!r})"
        )