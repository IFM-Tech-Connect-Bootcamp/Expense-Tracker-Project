"""Data Transfer Objects for User Management application layer.

This module contains DTOs used to transfer data between
application layer and external consumers.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(frozen=True)
class UserDTO:
    """Data Transfer Object for User entity.
    
    This DTO represents a user in a serializable format
    suitable for API responses and inter-layer communication.
    """
    id: str
    email: str
    first_name: str
    last_name: str
    status: str
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True)
class AuthResultDTO:
    """Data Transfer Object for authentication results.
    
    This DTO contains the result of authentication operations
    including user information and access tokens.
    """
    user: UserDTO
    access_token: str
    token_type: str = "Bearer"
    expires_in: Optional[int] = None