"""Authenticate user handler.

This module contains the handler for user authentication use cases.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Protocol

from django.conf import settings

from ...domain.errors import UserManagementDomainError
from ...domain.repositories.user_repository import UserRepository
from ...domain.services.password_policy import TokenProvider
from ...domain.value_objects.email import Email
from ..commands.authenticate_user import AuthenticateUserCommand
from ..dto import AuthResultDTO, UserDTO
from ..errors import translate_domain_error

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


class PasswordService(Protocol):
    """Protocol for password service operations."""
    
    async def hash_password(self, password: str) -> str:
        """Hash a password."""
        ...
    
    async def verify_password(self, password: str, hashed: str) -> bool:
        """Verify a password against its hash."""
        ...


class AuthenticateUserHandler:
    """Handler for user authentication operations.
    
    This handler orchestrates the user authentication use case by:
    1. Validating the authentication request
    2. Finding the user by email
    3. Verifying the password
    4. Checking user account status
    5. Generating an authentication token
    6. Returning an authentication result DTO
    """
    
    def __init__(
        self,
        user_repository: UserRepository,
        password_service: PasswordService,
        token_provider: TokenProvider,
    ) -> None:
        """Initialize the authenticate user handler.
        
        Args:
            user_repository: Repository for user persistence operations.
            password_service: Service for password verification operations.
            token_provider: Service for JWT token generation.
        """
        self._user_repository = user_repository
        self._password_service = password_service
        self._token_provider = token_provider
    
    async def handle(self, command: AuthenticateUserCommand) -> AuthResultDTO:
        """Execute the user authentication use case.
        
        Args:
            command: The authentication command containing credentials.
            
        Returns:
            AuthResultDTO containing the token and user information.
            
        Raises:
            ApplicationError: If authentication fails for any reason.
        """
        logger.info(f"Executing user authentication for email: {command.email}")
        
        try:
            # Create domain value object
            email = Email(command.email)
            
            # Find user by email
            user = await self._user_repository.find_by_email(email)
            if user is None:
                logger.warning(f"Authentication failed: User not found: {command.email}")
                from ...domain.errors import InvalidCredentialsError
                raise InvalidCredentialsError(email.value)
            
            # Verify password
            current_hash = user.password_hash.value if hasattr(user.password_hash, 'value') else user.password_hash
            is_valid = await self._password_service.verify_password(
                command.password, 
                current_hash
            )
            if not is_valid:
                logger.warning(f"Authentication failed: Invalid password for email: {command.email}")
                from ...domain.errors import InvalidCredentialsError
                raise InvalidCredentialsError(email.value)
            
            # Check if user is active (business rule validation)
            if not user.is_active():
                logger.warning(f"Authentication failed: User is not active: {command.email}")
                from ...domain.errors import UserDeactivatedError
                raise UserDeactivatedError(user.id.value)
            
            # Generate JWT token using the token provider
            logger.info(f"Generating JWT token for user: {command.email}")
            access_token = await self._token_provider.issue_token(user.id)
            
            logger.info(f"User successfully authenticated: {user.id.value}")
            
            # Create user DTO
            try:
                user_dto = UserDTO(
                    id=str(user.id.value),
                    email=user.email.value,
                    first_name=user.first_name.value,
                    last_name=user.last_name.value,
                    full_name=f"{user.first_name.value} {user.last_name.value}",
                    status=user.status.value,
                    created_at=user.created_at,
                    updated_at=user.updated_at
                )
            except Exception as e:
                logger.error(f"Failed to create UserDTO: {e}")
                raise ValueError(f"Failed to create user DTO: {e}") from e
            
            # Return authentication result
            try:
                auth_result = AuthResultDTO(
                    user=user_dto,
                    access_token=access_token,
                    expires_in=settings.JWT_SETTINGS['ACCESS_TOKEN_LIFETIME']
                )
                return auth_result
            except Exception as e:
                logger.error(f"Failed to create AuthResultDTO: {e}")
                raise ValueError(f"Failed to create auth result: {e}") from e
            
        except UserManagementDomainError as e:
            logger.error(f"Domain error during authentication: {e}")
            raise translate_domain_error(e) from e
        except ValueError as e:
            logger.error(f"Validation error during authentication: {e}")
            # Convert to domain error for consistent handling
            from ...domain.errors import InvalidCredentialsError
            raise InvalidCredentialsError(command.email) from e
        except Exception as e:
            logger.error(f"Unexpected error during authentication: {e}", exc_info=True)
            # Re-raise as domain error to maintain error handling consistency
            from ...domain.errors import InvalidCredentialsError
            raise InvalidCredentialsError(command.email) from e