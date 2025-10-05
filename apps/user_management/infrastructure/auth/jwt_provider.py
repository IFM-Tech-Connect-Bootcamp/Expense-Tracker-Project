"""JWT token provider implementation.

This module provides JWT token generation and verification
for user authentication using PyJWT library.
"""

from __future__ import annotations

import logging
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

# Import required libraries
import jwt
from django.conf import settings

from ...domain.services.password_policy import TokenProvider
from ...domain.value_objects.user_id import UserId

logger = logging.getLogger(__name__)


class JWTTokenProvider(TokenProvider):
    """JWT implementation of TokenProvider domain service.
    
    Provides secure JWT token generation and verification
    for user authentication and session management.
    """

    def __init__(
        self,
        secret_key: Optional[str] = None,
        algorithm: str = "HS256",
        expiry_minutes: int = 60,
        issuer: str = "expense-tracker",
    ) -> None:
        """Initialize JWT token provider.
        
        Args:
            secret_key: JWT signing secret. If None, uses Django settings.
            algorithm: JWT signing algorithm. Default: HS256.
            expiry_minutes: Token expiration time in minutes. Default: 60.
            issuer: Token issuer claim. Default: expense-tracker.
            
        Raises:
            ValueError: If secret_key is empty or algorithm is unsupported.
        """
        self._secret_key = secret_key or getattr(settings, 'JWT_SECRET_KEY', None)
        if not self._secret_key:
            raise ValueError("JWT secret key is required")
        
        if algorithm not in ['HS256', 'HS384', 'HS512', 'RS256', 'RS384', 'RS512']:
            raise ValueError(f"Unsupported JWT algorithm: {algorithm}")
        
        self._algorithm = algorithm
        self._expiry_minutes = max(1, expiry_minutes)  # Minimum 1 minute
        self._issuer = issuer
        
        logger.debug(
            f"Initialized JWTTokenProvider: algorithm={algorithm}, "
            f"expiry={expiry_minutes}min, issuer={issuer}"
        )

    async def issue_token(self, user_id: UserId, claims: Optional[Dict[str, Any]] = None) -> str:
        """Issue a JWT token for the specified user.
        
        Args:
            user_id: User ID to include in token.
            claims: Optional additional claims to include.
            
        Returns:
            Signed JWT token string.
            
        Raises:
            ValueError: If token generation fails.
        """
        logger.debug(f"Issuing JWT token for user: {user_id.value}")
        
        try:
            now = datetime.now(timezone.utc)
            expiry = now + timedelta(minutes=self._expiry_minutes)
            
            # Standard JWT claims
            payload = {
                'sub': str(user_id.value),  # Subject (user ID)
                'iss': self._issuer,        # Issuer
                'iat': int(now.timestamp()),  # Issued at
                'exp': int(expiry.timestamp()),  # Expiration
                'jti': str(uuid.uuid4()),   # JWT ID (unique identifier)
            }
            
            # Add custom claims if provided
            if claims:
                # Validate that custom claims don't override standard claims
                reserved_claims = {'sub', 'iss', 'iat', 'exp', 'jti'}
                for claim in claims:
                    if claim in reserved_claims:
                        logger.warning(f"Ignoring reserved claim: {claim}")
                        continue
                    payload[claim] = claims[claim]
            
            # Generate and sign token
            token = jwt.encode(payload, self._secret_key, algorithm=self._algorithm)
            
            logger.debug(f"Successfully issued JWT token for user: {user_id.value}")
            return token
            
        except Exception as e:
            logger.error(f"Failed to issue JWT token for user {user_id.value}: {e}")
            raise ValueError(f"Token generation failed: {e}") from e

    async def verify_token(self, token: str) -> UserId:
        """Verify a JWT token and extract user ID.
        
        Args:
            token: JWT token string to verify.
            
        Returns:
            User ID extracted from token.
            
        Raises:
            ValueError: If token is invalid, expired, or verification fails.
        """
        if not token:
            raise ValueError("Token cannot be empty")
        
        logger.debug("Verifying JWT token")
        
        try:
            # Decode and verify token
            payload = jwt.decode(
                token,
                self._secret_key,
                algorithms=[self._algorithm],
                issuer=self._issuer,
                options={
                    'verify_signature': True,
                    'verify_exp': True,
                    'verify_iat': True,
                    'verify_iss': True,
                    'require': ['sub', 'iss', 'iat', 'exp']
                }
            )
            
            # Extract user ID
            user_id_str = payload.get('sub')
            if not user_id_str:
                raise ValueError("Token missing user ID (sub claim)")
            
            try:
                user_id = UserId(uuid.UUID(user_id_str))
            except (ValueError, TypeError) as e:
                raise ValueError(f"Invalid user ID in token: {e}") from e
            
            logger.debug(f"Successfully verified JWT token for user: {user_id.value}")
            return user_id
            
        except jwt.ExpiredSignatureError:
            logger.debug("JWT token has expired")
            raise ValueError("Token has expired")
        except jwt.InvalidIssuerError:
            logger.debug("JWT token has invalid issuer")
            raise ValueError("Token has invalid issuer")
        except jwt.InvalidSignatureError:
            logger.debug("JWT token has invalid signature")
            raise ValueError("Token signature is invalid")
        except jwt.InvalidTokenError as e:
            logger.debug(f"JWT token is invalid: {e}")
            raise ValueError(f"Token is invalid: {e}") from e
        except Exception as e:
            logger.error(f"JWT token verification failed: {e}")
            raise ValueError(f"Token verification failed: {e}") from e

    async def refresh_token(self, token: str) -> str:
        """Refresh a JWT token with new expiration.
        
        Args:
            token: Current JWT token to refresh.
            
        Returns:
            New JWT token with extended expiration.
            
        Raises:
            ValueError: If token is invalid or refresh fails.
        """
        logger.debug("Refreshing JWT token")
        
        try:
            # Verify current token (but allow expired tokens for refresh)
            payload = jwt.decode(
                token,
                self._secret_key,
                algorithms=[self._algorithm],
                issuer=self._issuer,
                options={
                    'verify_signature': True,
                    'verify_exp': False,  # Allow expired tokens for refresh
                    'verify_iat': True,
                    'verify_iss': True,
                    'require': ['sub', 'iss', 'iat']
                }
            )
            
            # Extract user ID and custom claims
            user_id_str = payload.get('sub')
            if not user_id_str:
                raise ValueError("Token missing user ID")
            
            user_id = UserId(uuid.UUID(user_id_str))
            
            # Extract custom claims (exclude standard JWT claims)
            custom_claims = {
                k: v for k, v in payload.items()
                if k not in ['sub', 'iss', 'iat', 'exp', 'jti']
            }
            
            # Issue new token
            new_token = await self.issue_token(user_id, custom_claims)
            
            logger.debug(f"Successfully refreshed JWT token for user: {user_id.value}")
            return new_token
            
        except Exception as e:
            logger.error(f"JWT token refresh failed: {e}")
            raise ValueError(f"Token refresh failed: {e}") from e

    def get_token_expiry(self, token: str) -> Optional[datetime]:
        """Get expiration time from JWT token.
        
        Args:
            token: JWT token to inspect.
            
        Returns:
            Token expiration datetime, or None if invalid.
        """
        try:
            # Decode without verification to get expiry
            payload = jwt.decode(token, options={"verify_signature": False})
            exp_timestamp = payload.get('exp')
            if exp_timestamp:
                return datetime.fromtimestamp(exp_timestamp, tz=timezone.utc)
            return None
        except Exception:
            return None

    @property
    def expiry_minutes(self) -> int:
        """Get token expiration time in minutes."""
        return self._expiry_minutes

    @property
    def algorithm(self) -> str:
        """Get JWT signing algorithm."""
        return self._algorithm

    @property
    def issuer(self) -> str:
        """Get JWT issuer."""
        return self._issuer


# Factory function for dependency injection
def create_jwt_provider(
    secret_key: Optional[str] = None,
    expiry_minutes: int = 60
) -> JWTTokenProvider:
    """Create a JWT token provider with specified configuration.
    
    Args:
        secret_key: JWT signing secret. If None, uses Django settings.
        expiry_minutes: Token expiration time in minutes.
        
    Returns:
        Configured JWT token provider instance.
    """
    return JWTTokenProvider(
        secret_key=secret_key,
        expiry_minutes=expiry_minutes
    )