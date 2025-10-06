"""
Authentication components for the User Management API.

This module provides JWT authentication middleware and utilities
for the presentation layer, integrating with the infrastructure
layer's token provider.
"""

from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.request import Request
from django.contrib.auth.models import AnonymousUser
from django.http import HttpRequest
from typing import Optional, Tuple, Any
import logging

from ..infrastructure.container import InfrastructureContainer
from ..domain.entities import User
from ..domain.errors import UserDeactivatedError, UserNotFoundError
from ..domain.repositories.user_repository import UserRepository
from ..domain.services.password_policy import TokenProvider


logger = logging.getLogger(__name__)


class UserProxy:
    """
    Proxy class to adapt domain User entity to Django's expected user interface.
    
    This allows Django REST Framework to work with our domain entities
    without breaking clean architecture principles.
    """
    
    def __init__(self, user: User):
        self.user = user
        self._id = user.id
        self.email = user.email
        self.first_name = user.first_name
        self.last_name = user.last_name
        self.is_active = user.status == "ACTIVE"
        self.is_authenticated = True
        self.is_anonymous = False

    @property
    def pk(self):
        """Primary key for Django compatibility."""
        return self._id

    @property
    def id(self):
        """User ID property."""
        return self._id

    def __str__(self):
        return self.email

    def __eq__(self, other):
        """Equality comparison for user objects."""
        if isinstance(other, UserProxy):
            return self._id == other._id
        return False

    def __hash__(self):
        """Hash method for user objects."""
        return hash(self._id)


class JWTAuthentication(BaseAuthentication):
    """
    JWT authentication backend for Django REST Framework.
    
    This class integrates the infrastructure layer's JWT token provider
    with Django REST Framework's authentication system.
    """
    
    keyword = 'Bearer'
    
    def __init__(self):
        self.container = InfrastructureContainer()
        self.token_provider = self.container.get(TokenProvider)
        self.user_repository = self.container.get(UserRepository)

    def authenticate(self, request: Request) -> Optional[Tuple[UserProxy, str]]:
        """
        Authenticate the request using JWT token.
        
        Args:
            request: The HTTP request object
            
        Returns:
            Tuple of (user, token) if authentication successful, None otherwise
            
        Raises:
            AuthenticationFailed: If authentication fails
        """
        header = self.get_authorization_header(request)
        if not header:
            return None
            
        try:
            token = self.get_token_from_header(header)
            if not token:
                return None
                
            return self._authenticate_token(token)
            
        except ValueError as e:
            logger.warning(f"Authentication failed: {str(e)}")
            raise AuthenticationFailed(f"Invalid token: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected authentication error: {str(e)}")
            raise AuthenticationFailed("Authentication failed")

    async def authenticate_async(self, request: Request) -> Optional[Tuple[UserProxy, str]]:
        """
        Async version of authenticate for async views.
        
        Args:
            request: The HTTP request object
            
        Returns:
            Tuple of (user, token) if authentication successful, None otherwise
        """
        header = self.get_authorization_header(request)
        if not header:
            return None
            
        try:
            token = self.get_token_from_header(header)
            if not token:
                return None
                
            return await self._authenticate_token_async(token)
            
        except ValueError as e:
            logger.warning(f"Async authentication failed: {str(e)}")
            raise AuthenticationFailed(f"Invalid token: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected async authentication error: {str(e)}")
            raise AuthenticationFailed("Authentication failed")

    def get_authorization_header(self, request: Request) -> Optional[bytes]:
        """
        Extract authorization header from request.
        
        Args:
            request: The HTTP request object
            
        Returns:
            Authorization header bytes or None
        """
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        if not auth_header:
            return None
            
        if isinstance(auth_header, str):
            auth_header = auth_header.encode('utf-8')
            
        return auth_header

    def get_token_from_header(self, header: bytes) -> Optional[str]:
        """
        Extract JWT token from authorization header.
        
        Args:
            header: Authorization header bytes
            
        Returns:
            JWT token string or None
        """
        try:
            header_str = header.decode('utf-8')
            parts = header_str.split()
            
            if len(parts) != 2:
                return None
                
            keyword, token = parts
            if keyword.lower() != self.keyword.lower():
                return None
                
            return token
            
        except (UnicodeDecodeError, ValueError):
            return None

    def _authenticate_token(self, token: str) -> Tuple[UserProxy, str]:
        """
        Authenticate token and return user (sync version).
        
        Args:
            token: JWT token string
            
        Returns:
            Tuple of (UserProxy, token)
            
        Raises:
            AuthenticationFailed: If token is invalid or user not found
        """
        try:
            import asyncio
            from asgiref.sync import sync_to_async
            
            # Run the async authentication in the sync context
            # This is needed because DRF authentication is synchronous
            async def async_auth():
                return await self._authenticate_token_async(token)
            
            # Get or create event loop and run the async authentication
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # If we're already in an event loop, we need to use a different approach
                    # Create a new thread with its own event loop
                    import concurrent.futures
                    import threading
                    
                    def run_in_new_loop():
                        new_loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(new_loop)
                        try:
                            return new_loop.run_until_complete(async_auth())
                        finally:
                            new_loop.close()
                    
                    with concurrent.futures.ThreadPoolExecutor() as executor:
                        future = executor.submit(run_in_new_loop)
                        return future.result(timeout=10)  # 10 second timeout
                else:
                    return loop.run_until_complete(async_auth())
            except RuntimeError:
                # No event loop, create one
                return asyncio.run(async_auth())
                
        except Exception as e:
            raise AuthenticationFailed(f"Authentication failed: {str(e)}")

    async def _authenticate_token_async(self, token: str) -> Tuple[UserProxy, str]:
        """
        Authenticate token and return user (async version).
        
        Args:
            token: JWT token string
            
        Returns:
            Tuple of (UserProxy, token)
            
        Raises:
            AuthenticationFailed: If token is invalid or user not found
        """
        # Verify the JWT token and get user ID
        try:
            user_id = await self.token_provider.verify_token(token)
        except Exception as e:
            raise AuthenticationFailed(f"Token verification failed: {str(e)}")
        
        # Get user from repository
        try:
            user = await self.user_repository.find_by_id(user_id)
            if not user:
                raise AuthenticationFailed("User not found")
            
            if not user.is_active():
                raise AuthenticationFailed("User account is not active")
                
            user_proxy = UserProxy(user)
            return user_proxy, token
            
        except Exception as e:
            if "User not found" in str(e) or "not active" in str(e):
                raise
            raise AuthenticationFailed(f"User lookup failed: {str(e)}")

    def authenticate_header(self, request: Request) -> str:
        """
        Return authentication header for 401 responses.
        
        Args:
            request: The HTTP request object
            
        Returns:
            Authentication header string
        """
        return self.keyword


def get_current_user_from_request(request: HttpRequest) -> Optional[User]:
    """
    Extract the current authenticated user from request.
    
    Args:
        request: Django HTTP request object
        
    Returns:
        Current User entity or None if not authenticated
    """
    if hasattr(request, 'user') and isinstance(request.user, UserProxy):
        return request.user.user
    return None